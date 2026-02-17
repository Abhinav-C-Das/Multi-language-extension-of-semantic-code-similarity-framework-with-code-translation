import scala.collection.mutable
import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._

importCpg("cpg.bin")
val targetFile =
  sys.env.getOrElse(
    "TARGET_FILE",
    throw new RuntimeException("TARGET_FILE not set")
  )

// Restrict to this file only (CRITICAL)
val methods =
  cpg.method.filter(m => m.filename.endsWith(targetFile)).l

def jsonNum(x: Double): String =
  if (x.isNaN || x.isInfinity) "0" else x.toString

val result = mutable.LinkedHashMap[String, String]()

// =======================================================
// 1. DEF–USE EDGES (INTRA-PROCEDURAL, LOCAL ONLY)
// =======================================================
//
// We do NOT use PDG / dataflow.
// We use symbol resolution already present in the AST.

val defUseEdges =
  methods.flatMap { m =>
    m.local.flatMap { l =>
      l.referencingIdentifiers.map(id => (l.id, id.id))
    }
  }.distinct.size

result("def_use_edges") = defUseEdges.toString

val varUses =
  methods.flatMap(_.local.referencingIdentifiers).size

val defUseDensity =
  if (varUses > 0) defUseEdges.toDouble / varUses else 0.0

result("def_use_density") = jsonNum(defUseDensity)

// =======================================================
// 2. CONTROL PREDICATES
// =======================================================

val controlPredicates =
  methods.map { m =>
    m.controlStructure.count(cs =>
      cs.controlStructureType match {
        case "IF" | "SWITCH" | "FOR" | "WHILE" | "DO" => true
        case _                                       => false
      }
    )
  }.sum

result("control_predicates") = controlPredicates.toString

val controlDataRatio =
  if (defUseEdges > 0)
    controlPredicates.toDouble / defUseEdges
  else 0.0

result("control_data_ratio") = jsonNum(controlDataRatio)

// =======================================================
// 3. PARAMETER → RETURN (AST-BASED, CONSERVATIVE)
// =======================================================

val params =
  methods.flatMap(_.parameter.l)

val returns =
  methods.flatMap(_.ast.isReturn.l)

val paramsMentionedInReturn =
  params.count { p =>
    returns.exists(_.ast.isIdentifier.nameExact(p.name).nonEmpty)
  }

val paramReturnRatio =
  if (params.nonEmpty)
    paramsMentionedInReturn.toDouble / params.size
  else 0.0

result("param_return_ratio") = jsonNum(paramReturnRatio)

// =======================================================
// 4. PARAMETER → OUTPUT (AST-BASED)
// =======================================================

val outputCalls =
  cpg.call.nameExact("printf", "puts", "putchar").l

val paramsReachingOutput =
  params.count { p =>
    p.referencingIdentifiers.exists { id =>
      outputCalls.exists(call =>
        id.astParent.exists(_.id == call.id)
      )
    }
  }

val paramOutputRatio =
  if (params.nonEmpty)
    paramsReachingOutput.toDouble / params.size
  else 0.0

result("param_output_ratio") = jsonNum(paramOutputRatio)

// =======================================================
// OUTPUT
// =======================================================

println("{")
result.zipWithIndex.foreach { case ((k, v), i) =>
  val comma = if (i < result.size - 1) "," else ""
  println(s"""  "$k": $v$comma""")
}
println("}")

