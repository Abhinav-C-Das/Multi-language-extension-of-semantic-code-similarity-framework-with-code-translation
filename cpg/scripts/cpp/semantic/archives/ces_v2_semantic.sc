importCpg("cpg.bin")

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.io.Source
import java.io.File

// =======================================================
// CES V2 - ENHANCED SEMANTIC PATTERNS
// 
// IMPROVEMENTS OVER V1:
// 1. Loop context normalization (loop_ANY instead of loop_FOR/WHILE/DO)
// 2. Optimization flag filtering (skip noise patterns)
// 3. Pattern importance weighting
// 4. Enhanced algorithmic abstraction
// =======================================================

// =======================================================
// SAFE CANONICALIZATION LOADER
// =======================================================
def loadCanonicalMap(): Map[String, Map[String, String]] = {
  val f = new File("canonical.json")
  if (!f.exists()) {
    return Map.empty
  }

  val rawText =
    try {
      Source.fromFile(f, "ISO-8859-1").mkString
    } catch {
      case _: Throwable =>
        return Map.empty
    }

  val text = rawText.replaceAll("[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F]", "")
  val out = mutable.Map[String, Map[String, String]]()

  val methodRegex = "\"([^\"]+)\"\\s*:\\s*\\{([^}]*)\\}".r
  val varRegex    = "\"([^\"]+)\"\\s*:\\s*\"([^\"]+)\"".r

  for (m <- methodRegex.findAllMatchIn(text)) {
    val method = m.group(1)
    val body   = m.group(2)
    val vars = varRegex.findAllMatchIn(body).map(v => v.group(1) -> v.group(2)).toMap
    if (vars.nonEmpty) out(method) = vars
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
// CES V2 RECORD (with importance weight)
// =======================================================
case class CESRecord(
  context: String,
  variable: String,
  evolution: String,
  operator: String,
  importance: Double  // NEW: Pattern importance weight (0.0-1.0)
)

val cesRecords = mutable.ListBuffer[CESRecord]()

// =======================================================
// OPTIMIZATION FLAG DETECTION
// =======================================================
val OPTIMIZATION_FLAG_NAMES = Set(
  "swapped", "done", "found", "changed", "modified",
  "flag", "check", "visited", "seen", "updated"
)

def isOptimizationFlag(varName: String): Boolean = {
  val lower = varName.toLowerCase
  OPTIMIZATION_FLAG_NAMES.exists(flag => lower.contains(flag))
}

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
// LOOP CES V2 - NORMALIZED CONTEXTS
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

    // ✨ ENHANCEMENT 1: NORMALIZED LOOP CONTEXT
    // All loops treated as "loop_ANY" for algorithmic equivalence
    val loopContext = "loop_ANY"

    // === PATTERN: SEARCH_WITH_RETURN ===
    val returnNodes = loop.ast.isReturn.l
    for (ret <- returnNodes) {
      val isConditional = ret.inAst.isControlStructure
        .exists(cs => cs.controlStructureType == "IF")
      
      if (isConditional) {
        cesRecords += CESRecord(
          loopContext, 
          "RETURN", 
          "SEARCH_WITH_RETURN", 
          "EARLY_EXIT",
          1.0  // High importance - algorithmic pattern
        )
      }
    }

    // === PATTERN: COMPARISON_CHAIN ===
    val comparisons = loop.ast.isCall
      .filter(c =>
        c.name.contains("operator.equals") ||
        c.name.contains("operator.notEquals")
      )
      .l

    for (comp <- comparisons) {
      val args = comp.argument.code.l
      
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
          "SYMMETRIC",
          1.0  // High importance - core algorithm
        )
      }
    }

    val inductionVars = loop.condition.ast.isIdentifier.name.l.toSet

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
       
        val isNarrowingWindow =
          !isAccumulative &&
          !controlGuarded &&
          (lhs == "v0" || lhs == "v1") &&
          (rhs.contains("mid") || rhs.contains("m") || 
          rhs.contains("+") || rhs.contains("-"))

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

        // ✨ ENHANCEMENT 2: SKIP OPTIMIZATION FLAG PATTERNS
        val isOptFlag = isOptimizationFlag(rawLhs)
        
        // Determine importance weight
        val importance = if (isOptFlag) {
          0.0  // Filter out - don't record optimization flags
        } else if (isConditionalSwap || isNarrowingWindow) {
          1.0  // High importance - core algorithmic patterns
        } else if (isAccumulative) {
          0.9  // High importance - accumulation is core
        } else if (controlGuarded && (guardCond.exists(c => isMaxUpdate(rawLhs, c)) || 
                                      guardCond.exists(c => isMinUpdate(rawLhs, c)))) {
          0.8  // Medium-high - min/max patterns are important
        } else if (controlGuarded && !isOptFlag) {
          0.5  // Lower importance - generic guarded assignments (but not flags)
        } else {
          0.7  // Medium - recomputed
        }

        // Only record if importance > 0 (skip optimization flags)
        if (importance > 0.0) {
          if (isConditionalSwap) {
            cesRecords += CESRecord(loopContext, lhs, "CONDITIONAL_SWAP", "ASSIGN", importance)
          } else if (isNarrowingWindow) {
            cesRecords += CESRecord(loopContext, lhs, "NARROWING_WINDOW", "ASSIGN", importance)
          } else if (isAccumulative) {
            cesRecords += CESRecord(loopContext, lhs, "ACCUMULATIVE", op, importance)
          } else if (controlGuarded && guardCond.exists(c => isMaxUpdate(rawLhs, c))) {
            cesRecords += CESRecord(loopContext, lhs, "MAX_UPDATE", "COMPARE", importance)
          } else if (controlGuarded && guardCond.exists(c => isMinUpdate(rawLhs, c))) {
            cesRecords += CESRecord(loopContext, lhs, "MIN_UPDATE", "COMPARE", importance)
          } else if (controlGuarded) {
            // Generic guard - only include if not an optimization flag
            if (!isOptFlag) {
              cesRecords += CESRecord(loopContext, lhs, "CONTROL_GATED", "ASSIGN", importance)
            }
          } else {
            cesRecords += CESRecord(loopContext, lhs, "RECOMPUTED", "ASSIGN", importance)
          }
        }
      }
    }
  }

// =======================================================
// RECURSIVE CES V2
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
        cesRecords += CESRecord(s"rec_${name}", "return", "ACCUMULATIVE", "ADD", 1.0)
      } else {
        cesRecords += CESRecord(s"rec_${name}", "return", "RECOMPUTED", "ASSIGN", 0.9)
      }
    }
  }

// =======================================================
// OUTPUT JSON (WITH IMPORTANCE METADATA)
// =======================================================
println(
  jsonArr(
    cesRecords.map { r =>
      jsonObj(Seq(
        "context"    -> jsonStr(r.context),
        "evolution"  -> jsonStr(r.evolution),
        "operator"   -> jsonStr(r.operator),
        "importance" -> r.importance.toString  // NEW: importance weight
      ))
    }.toSeq
  )
)
