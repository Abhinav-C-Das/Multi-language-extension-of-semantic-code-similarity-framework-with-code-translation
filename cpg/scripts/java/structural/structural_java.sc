import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._

importCpg("cpg.bin")

val targetFile = sys.env.getOrElse("TARGET_FILE", "")

// Helper to format JSON map
def jsonMapInt(m: Map[String, Int]): String =
  m.map { case (k, v) => "\"" + k + "\": " + v }
    .mkString("{", ", ", "}")

def jsonMapDouble(m: Map[String, Double]): String =
  m.map { case (k, v) => "\"" + k + "\": " + v }
    .mkString("{", ", ", "}")

// Get all methods (filter by targetFile if needed, otherwise all non-external)
val methods = if (targetFile.nonEmpty) {
  cpg.method.filter(m => m.filename.endsWith(targetFile)).l
} else {
  cpg.method.filterNot(_.isExternal).l
}

// ============================================
// AST Metrics
// ============================================

val astNodes = methods.flatMap(_.ast.l)
val astNodeCount = astNodes.size

val astTypeHistogram =
  astNodes.groupBy(_.label).view.mapValues(_.size).toMap

// Recursive depth calculation like C version
def astDepth(n: AstNode): Int =
  if (n.astChildren.isEmpty) 1
  else 1 + n.astChildren.map(astDepth).max

val astDepths = astNodes.collect { case a: AstNode => astDepth(a) }
val maxAstDepth = astDepths.maxOption.getOrElse(0)
val avgAstDepth =
  if (astDepths.nonEmpty) astDepths.sum.toDouble / astDepths.size else 0.0

// ============================================
// CFG Metrics
// ============================================

val cfgNodes = methods.flatMap(_.cfgNode.l)
val cfgNodeCount = cfgNodes.size
val cfgEdgeCount = cfgNodes.flatMap(_.cfgNext).size

// ============================================
// Control Flow Metrics
// ============================================

val conditionalCount =
  methods.flatMap(_.controlStructure).count(cs =>
    cs.controlStructureType == "IF" || cs.controlStructureType == "SWITCH"
  )

val loopCount =
  methods.flatMap(_.controlStructure).count(cs =>
    cs.controlStructureType match {
      case "FOR" | "WHILE" | "DO" | "FOREACH" => true
      case _ => false
    }
  )

val ternaryCount =
  methods.flatMap(_.ast.isCall).count(call =>
    call.name == "<operator>.conditional"
  )

// ============================================
// Call Graph Metrics
// ============================================

val callCount = methods.flatMap(_.ast.isCall).size

val methodCallCount =
  methods.flatMap(_.ast.isCall).count(call =>
    !call.name.startsWith("<operator>")
  )

// ============================================
// Output JSON
// ============================================

println("{")
println(s"""  "ast_node_count": $astNodeCount,""")
println(s"""  "ast_type_histogram": ${jsonMapInt(astTypeHistogram)},""")
println(s"""  "max_ast_depth": $maxAstDepth,""")
println(s"""  "avg_ast_depth": $avgAstDepth,""")
println(s"""  "cfg_node_count": $cfgNodeCount,""")
println(s"""  "cfg_edge_count": $cfgEdgeCount,""")
println(s"""  "conditional_count": $conditionalCount,""")
println(s"""  "loop_count": $loopCount,""")
println(s"""  "ternary_count": $ternaryCount,""")
println(s"""  "call_count": $callCount,""")
println(s"""  "method_call_count": $methodCallCount""")
println("}")
