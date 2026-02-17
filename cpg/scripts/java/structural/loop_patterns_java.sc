importCpg("cpg.bin")

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.util.Try

// Detect enhanced for loops (for-each style)
val enhancedForLoops = cpg.method
  .filter(!_.isExternal)
  .controlStructure
  .filter(cs => cs.controlStructureType == "FOR")
  .filter { forLoop =>
    // Enhanced for uses ":" in condition
    val condCode = forLoop.condition.code.mkString(" ")
    condCode.contains(":")
  }
  .l

val hasEnhancedFor = if (enhancedForLoops.nonEmpty) 1 else 0
val enhancedForCount = enhancedForLoops.size

// Standard for loops (index-based)
val standardForLoops = cpg.method
  .filter(!_.isExternal)
  .controlStructure
  .filter(cs => cs.controlStructureType == "FOR")
  .filter { forLoop =>
    val condCode = forLoop.condition.code.mkString(" ")
    !condCode.contains(":") && (condCode.contains("<") || condCode.contains(">"))
  }
  .l

val hasStandardFor = if (standardForLoops.nonEmpty) 1 else 0
val standardForCount = standardForLoops.size

// Detect array access patterns in loops
val arrayAccessInLoops = cpg.method
  .filter(!_.isExternal)
  .controlStructure
  .filter(cs => cs.controlStructureType == "FOR")
  .flatMap(_.ast.isCall)
  .filter(c => c.name.contains("indexAccess") || c.name.contains("ArrayAccess"))
  .l
  .size

println(s"""{
  "has_enhanced_for_loop": $hasEnhancedFor,
  "enhanced_for_loop_count": $enhancedForCount,
  "has_standard_for_loop": $hasStandardFor,
  "standard_for_loop_count": $standardForCount,
  "array_index_access_count": $arrayAccessInLoops
}""")
