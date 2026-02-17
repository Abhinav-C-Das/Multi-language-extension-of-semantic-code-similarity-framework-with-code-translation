import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.io.Source
import java.io.File

importCpg("cpg.bin")

// =======================================================
// CES V2 - COMPUTATION EVOLUTION SIGNATURES (Java)
// =======================================================
// Based on C version with Java adaptations

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
// CES V2 RECORD
// =======================================================
case class CESRecord(
  context: String,
  variable: String,
  evolution: String,
  operator: String,
  importance: Double
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

    // Normalized loop context
    val loopContext = "loop_ANY"

    // PATTERN: SEARCH_WITH_RETURN
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
          1.0
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
      val lhs = canonVars.getOrElse(rawLhs, rawLhs)
      val rhs = assign.argument(2).code

      if (!inductionVars.contains(rawLhs)) {
        val evo = assign.name match {
          case "<operator>.assignmentPlus" => "ACCUMULATIVE"
          case "<operator>.assignmentMinus" => "DECREASING"
          case _ => if (rhs.contains(lhs)) "RECOMPUTED" else "SIMPLE_ASSIGNMENT"
        }

        val op = if (isControlGuarded(assign, loop)) "GUARDED" else "UNCONDITIONAL"

        cesRecords += CESRecord(
          loopContext,
          lhs,
          evo,
          op,
          0.8
        )
      }
    }
  }

// =======================================================
// NON-LOOP CES
// =======================================================
cpg.method
  .filterNot(_.isExternal)
  .foreach { m =>
    val canonVars = canonIdMap.getOrElse(m.name, Map())

    m.call
      .nameExact("<operator>.assignment", "<operator>.assignmentPlus")
      .filter(c => c.inAst.isControlStructure.isEmpty)
      .foreach { assign =>
        val rawLhs = assign.argument(1).code
        val lhs = canonVars.getOrElse(rawLhs, rawLhs)

        val evo = assign.name match {
          case "<operator>.assignmentPlus" => "SIMPLE_INCREMENT"
          case _ => "INITIALIZATION"
        }

        cesRecords += CESRecord(
          "global",
          lhs,
          evo,
          "DIRECT",
          0.5
        )
      }
  }

// =======================================================
// OUTPUT
// =======================================================
val json = cesRecords.map { r =>
  jsonObj(Seq(
    "context" -> jsonStr(r.context),
    "variable" -> jsonStr(r.variable),
    "evolution" -> jsonStr(r.evolution),
    "operator" -> jsonStr(r.operator),
    "importance" -> r.importance.toString
  ))
}

println(jsonArr(json))
