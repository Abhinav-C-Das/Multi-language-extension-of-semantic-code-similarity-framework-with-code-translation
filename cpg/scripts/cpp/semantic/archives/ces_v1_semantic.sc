importCpg("cpg.bin")

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.io.Source
import java.io.File

// =======================================================
// SAFE CANONICALIZATION LOADER (ENCODING-SAFE)
// =======================================================
def loadCanonicalMap(): Map[String, Map[String, String]] = {
  val f = new File("canonical.json")
  if (!f.exists()) {
    return Map.empty
  }

  val rawText =
    try {
      // ISO-8859-1 never throws on bytes
      Source.fromFile(f, "ISO-8859-1").mkString
    } catch {
      case _: Throwable =>
        return Map.empty
    }

  // Remove control characters except newline / tab
  val text = rawText.replaceAll("[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F]", "")

  val out = mutable.Map[String, Map[String, String]]()

  val methodRegex = "\"([^\"]+)\"\\s*:\\s*\\{([^}]*)\\}".r
  val varRegex    = "\"([^\"]+)\"\\s*:\\s*\"([^\"]+)\"".r

  for (m <- methodRegex.findAllMatchIn(text)) {
    val method = m.group(1)
    val body   = m.group(2)

    val vars =
      varRegex.findAllMatchIn(body)
        .map(v => v.group(1) -> v.group(2))
        .toMap

    if (vars.nonEmpty)
      out(method) = vars
  }

  out.toMap
}

val canonIdMap = loadCanonicalMap()

// =======================================================
// JSON HELPERS
// =======================================================
def jsonStr(s: String): String =
  "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

def jsonObj(fields: Seq[(String, String)]): String =
  fields.map { case (k, v) => jsonStr(k) + ": " + v }
    .mkString("{", ", ", "}")

def jsonArr(items: Seq[String]): String =
  items.mkString("[", ", ", "]")

// =======================================================
// CES RECORD
// =======================================================
case class CESRecord(
  context: String,
  variable: String,
  evolution: String,
  operator: String
)

val cesRecords = mutable.ListBuffer[CESRecord]()

// =======================================================
// HELPERS
// =======================================================
def isControlGuarded(assign: Call, loop: ControlStructure): Boolean =
  loop.ast
    .isControlStructure
    .filter(cs =>
      cs.controlStructureType == "IF" ||
      cs.controlStructureType == "SWITCH"
    )
    .exists(_.ast.contains(assign))

def getGuardCondition(assign: Call, loop: ControlStructure): Option[String] =
  loop.ast
    .isControlStructure
    .filter(cs =>
      cs.controlStructureType == "IF" ||
      cs.controlStructureType == "SWITCH"
    )
    .find(_.ast.contains(assign))
    .map(_.condition.code.mkString(" "))

def isMaxUpdate(lhs: String, cond: String): Boolean =
  cond.contains(lhs) && cond.contains(">")

def isMinUpdate(lhs: String, cond: String): Boolean =
  cond.contains(lhs) && cond.contains("<")

// =======================================================
// LOOP CES (SEMANTICS UNCHANGED)
// =======================================================
cpg.controlStructure
  .filter(cs =>
    cs.controlStructureType == "FOR" ||
    cs.controlStructureType == "WHILE" ||
    cs.controlStructureType == "DO"
  )
  .foreach { loop =>

    val method = loop.method
    val canonVars = canonIdMap.getOrElse(method.name, Map())

    val loopContext = s"loop_${loop.controlStructureType}"
        // === NEW PATTERN: SEARCH_WITH_RETURN ===
    // Detect early exit from search loops
    val returnNodes = loop.ast.isReturn.l
    for (ret <- returnNodes) {
      val returnValue = ret.argumentOut.headOption.map(_.code).getOrElse("UNKNOWN")
      
      // Check if return is conditional (inside IF)
      val isConditional = ret.inAst.isControlStructure
        .exists(cs => cs.controlStructureType == "IF")
      
      if (isConditional) {
        cesRecords += CESRecord(
          loopContext, 
          "RETURN", 
          "SEARCH_WITH_RETURN", 
          "EARLY_EXIT"
        )
      }
    }

    // === NEW PATTERN: COMPARISON_CHAIN ===
    // Detect symmetric comparison patterns (palindrome, reversal validation)
    val comparisons = loop.ast.isCall
      .filter(c =>
        c.name.contains("operator.equals") ||
        c.name.contains("operator.notEquals")
      )
      .l

    for (comp <- comparisons) {
      val args = comp.argument.code.l
      
      // Look for symmetric array/string access patterns
      // Must have BOTH forward and backward indexing
      val hasSymmetricAccess = 
        args.exists(a => a.contains("[i]") || a.contains("[left]") || a.contains("[start]")) &&
        args.exists(a => 
          a.contains("[n-i-1]") || a.contains("[n-1-i]") || 
          a.contains("[right]") || a.contains("[end]") ||
          (a.contains("len") && a.contains("-i")) ||
          (a.contains("length") && a.contains("-i"))
        )
      
      if (hasSymmetricAccess) {
        cesRecords += CESRecord(
          loopContext,
          "COMPARISON",
          "COMPARISON_CHAIN",
          "SYMMETRIC"
        )
      }
    }
    val inductionVars =
      loop.condition.ast.isIdentifier.name.l.toSet

    val assignments =
      loop.ast
        .isCall
        .filter(c =>
          c.name == "<operator>.assignment" ||
          c.name == "<operator>.assignmentPlus" ||
          c.name == "<operator>.assignmentMinus"
        )
        .l

    assignments.foreach { assign =>
      val rawLhs = assign.argument(1).code
      val rhs    = assign.argument(2).code
      val lhs    = canonVars.getOrElse(rawLhs, rawLhs)

      if (!inductionVars.contains(rawLhs)) {

        val op =
          assign.name match {
            case "<operator>.assignmentPlus"  => "ADD"
            case "<operator>.assignmentMinus" => "SUB"
            case "<operator>.assignmentMultiplication" => "MUL"
            case "<operator>.assignmentDivision" => "DIV"
            case _ => "ASSIGN"
          }

        val isAccumulative =
          rhs.contains(rawLhs) ||
          assign.name == "<operator>.assignmentPlus" ||
          assign.name == "<operator>.assignmentMinus" ||
          assign.name == "<operator>.assignmentMultiplication" ||
          assign.name == "<operator>.assignmentDivision"

        val controlGuarded = isControlGuarded(assign, loop)
        val guardCond = getGuardCondition(assign, loop)
       
        // Detect narrowing window pattern using canonicalized names
        val isNarrowingWindow =
          !isAccumulative &&
          !controlGuarded &&
          (lhs == "v0" || lhs == "v1") &&  // First two vars in binary search are window bounds
          (rhs.contains("mid") || rhs.contains("m") || 
          rhs.contains("+") || rhs.contains("-"))
                // === NEW PATTERN: CONDITIONAL_SWAP ===
        // Detect swap operations under conditional guards (sorting)
        val isConditionalSwap =
          !isAccumulative &&
          !isNarrowingWindow &&
          controlGuarded &&
          guardCond.exists(c => 
            c.contains(">") || c.contains("<") || 
            c.contains(">=") || c.contains("<=")
          ) &&
          (rawLhs == "temp" || rawLhs == "t" || rawLhs == "tmp" ||
           rawLhs == "swap" || rawLhs == "temp_val" || rawLhs == "tempVal")

        if (isConditionalSwap) {
          cesRecords += CESRecord(loopContext, lhs, "CONDITIONAL_SWAP", "ASSIGN")
        } else if (isNarrowingWindow){
          cesRecords += CESRecord(loopContext, lhs, "NARROWING_WINDOW", "ASSIGN")
        } else if (isAccumulative) {
          cesRecords += CESRecord(loopContext, lhs, "ACCUMULATIVE", op)
        } else if (controlGuarded && guardCond.exists(c => isMaxUpdate(rawLhs, c))) {
          cesRecords += CESRecord(loopContext, lhs, "MAX_UPDATE", "COMPARE")
        } else if (controlGuarded && guardCond.exists(c => isMinUpdate(rawLhs, c))) {
          cesRecords += CESRecord(loopContext, lhs, "MIN_UPDATE", "COMPARE")
        } else if (controlGuarded) {
          cesRecords += CESRecord(loopContext, lhs, "CONTROL_GATED", "ASSIGN")
        } else {
          cesRecords += CESRecord(loopContext, lhs, "RECOMPUTED", "ASSIGN")
        }
      }
    }
  }

// =======================================================
// RECURSIVE CES (UNCHANGED)
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>

    val name = method.name
    val calls = method.ast.isCall.l
    val recursive = calls.filter(_.name == name)

    if (recursive.nonEmpty) {

      val accumulative =
        calls.exists(c =>
          (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
          c.code.contains(name + "(")
        )

      if (accumulative) {
        cesRecords += CESRecord(s"rec_${name}", "return", "ACCUMULATIVE", "ADD")
      } else {
        cesRecords += CESRecord(s"rec_${name}", "return", "RECOMPUTED", "ASSIGN")
      }
    }
  }

// =======================================================
// OUTPUT JSON (TYPE-SAFE)
// =======================================================
println(
  jsonArr(
    cesRecords.map { r =>
      jsonObj(Seq(
        "context"   -> jsonStr(r.context),
        // "variable" removed - not needed for similarity
        "evolution" -> jsonStr(r.evolution),
        "operator"  -> jsonStr(r.operator)
      ))
    }.toSeq
  )
)
