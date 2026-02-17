// =======================================================
// JAVA CANONICALIZATION METADATA
// =======================================================
// Adapted from C canonicalization for Java-specific constructs

import scala.collection.mutable
import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._

importCpg("cpg.bin")

// Helper to bucket literals
def bucketLiteral(code: String): String = {
  if (code == "0") "ZERO"
  else if (code == "1") "ONE"
  else if (code.matches("-?\\d+")) {
    try {
      val n = code.toInt
      if (math.abs(n) <= 10) "SMALL_INT"
      else "LARGE_INT"
    } catch {
      case _: NumberFormatException => "LARGE_INT"
    }
  }
  else if (code.startsWith("\"")) "STRING"
  else if (code.startsWith("'")) "CHAR"
  else "CONST"
}

def jsonEscape(s: String): String =
  s.replace("\\", "\\\\")
   .replace("\"", "\\\"")
   .replace("\n", "\\n")
   .replace("\r", "\\r")
   .replace("\t", "\\t")

// -------------------------------------------------------
// IDENTIFIER CANONICALIZATION (METHOD-LOCAL, ORDERED)
// -------------------------------------------------------

val canonIdMap =
  mutable.LinkedHashMap[String, mutable.LinkedHashMap[String, String]]()

cpg.method
  .filter(m => !m.isExternal && m.name != "<global>")
  .foreach { m =>

    val localMap = mutable.LinkedHashMap[String, String]()
    var counter  = 0   // v0, v1, v2, ...

    val ids =
      m.ast
        .collectAll[Identifier]
        // only real variables: locals or parameters
        .filter { id =>
          id.refOut.exists {
            case _: Local     => true
            case _: MethodParameterIn => true
            case _            => false
          }
        }
        // declaration / first-use order
        .sortBy(id =>
          (id.lineNumber.getOrElse(Int.MaxValue),
           id.columnNumber.getOrElse(0))
        )
        .map(_.name)
        .distinct
        .l

    ids.foreach { name =>
      localMap(name) = s"v$counter"
      counter += 1
    }

    // Only store non-empty mappings
    if (localMap.nonEmpty) {
      val methodKey = m.name   // simplest, safest for educational code
      canonIdMap(methodKey) = localMap
    }
  }

// -------------------------------------------------------
// LITERAL BUCKETING
// -------------------------------------------------------

val canonLitMap =
  mutable.LinkedHashMap[String, String]()

cpg.literal.code.l.distinct.sorted.foreach { code =>
  canonLitMap(code) = bucketLiteral(code)
}

// -------------------------------------------------------
// JSON OUTPUT
// -------------------------------------------------------

println("{")

// identifiers
println("""  "identifiers": {""")
canonIdMap.toSeq.zipWithIndex.foreach { case ((method, vars), mi) =>
  println(s"""    "${jsonEscape(method)}": {""")
  vars.toSeq.zipWithIndex.foreach { case ((orig, canon), vi) =>
    val comma = if (vi < vars.size - 1) "," else ""
    println(s"""      "${jsonEscape(orig)}": "${canon}"$comma""")
  }
  val comma = if (mi < canonIdMap.size - 1) "," else ""
  println(s"""    }$comma""")
}
println("  },")

// literals
println("""  "literals": {""")
canonLitMap.toSeq.zipWithIndex.foreach { case ((orig, canon), li) =>
  val comma = if (li < canonLitMap.size - 1) "," else ""
  println(s"""    "${jsonEscape(orig)}": "${canon}"$comma""")
}
println("  }")

println("}")
