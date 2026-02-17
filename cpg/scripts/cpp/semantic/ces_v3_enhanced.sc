importCpg("cpg.bin")

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.io.Source
import java.io.File

// =======================================================
// CES V3 ENHANCED - ALL PRIORITY 1-4 FIXES IMPLEMENTED
// 
// ENHANCEMENTS OVER V3:
// Priority 1: Fixed recursion bugs, normalized contexts
// Priority 2: Tail recursion, recursive helpers, enhanced STL
// Priority 3: Direct formula, recursive binary search, better boundary checks
// Priority 4: Multi-function pattern analysis
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
  val varRegex    = "\"([^\"]+)\"\\s*:\"([^\"]+)\"".r

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
// CES RECORD (with importance weight)
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
// OPTIMIZATION FLAG DETECTION
// =======================================================
val OPTIMIZATION_FLAG_NAMES = Set(
  "swapped", "done", "found", "changed", "modified",
  "flag", "check", "visited", "seen", "updated"
)

val CONTAINER_APPEND_OPS = Set("push_back", "emplace_back", "add", "insert", "append")
val CONTAINER_ACCESS_OPS = Set("at", "get")

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
// PRIORITY 4: MULTI-FUNCTION LOOP ANALYSIS
// =======================================================
// Get all non-external methods
val allMethods = cpg.method.filter(!_.isExternal).l

// Track which methods are main vs helpers
val mainMethodNames = Set("main", "arraySum", "binarySearch", "reverseString", "isPrime", 
                          "findMax", "findMin", "bubbleSort", "selectionSort")
def isMainMethod(name: String): Boolean = 
  mainMethodNames.exists(m => name.toLowerCase.contains(m.toLowerCase))

// Analyze loops in ALL methods (not just top-level)
allMethods.foreach { method =>
  val methodName = method.name
  val isMain = isMainMethod(methodName)
  val canonVars = canonIdMap.getOrElse(methodName, Map())
  
  // Find loops in this method
  method.controlStructure
    .filter(cs =>
      cs.controlStructureType == "FOR" ||
      cs.controlStructureType == "WHILE" ||
      cs.controlStructureType == "DO"
    )
    .foreach { loop =>
      
      val loopContext = "loop_ANY"  // Normalized context
      
      // === PATTERN: SEARCH_WITH_RETURN ===
      val returnNodes = loop.ast.isReturn.l
      for (ret <- returnNodes) {
        val isConditional = ret.inAst.isControlStructure
          .exists(cs => cs.controlStructureType == "IF")
        
        if (isConditional) {
          val importance = if (isMain) 1.0 else 0.8
          cesRecords += CESRecord(
            loopContext, 
            "RETURN", 
            "SEARCH_WITH_RETURN", 
            "EARLY_EXIT",
            importance
          )
        }
      }

      // === PATTERN: CONDITIONAL_BREAK ===
      val breakNodes = loop.ast.isControlStructure.controlStructureType("BREAK").l
      for (brk <- breakNodes) {
        val isConditional = brk.inAst.isControlStructure
          .exists(cs => cs.controlStructureType == "IF")
        
        if (isConditional) {
          val importance = if (isMain) 1.0 else 0.8
          cesRecords += CESRecord(
            loopContext, 
            "RETURN",
            "SEARCH_WITH_RETURN",
            "EARLY_EXIT",         
            importance
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
          val importance = if (isMain) 1.0 else 0.8
          cesRecords += CESRecord(
            loopContext,
            "COMPARISON",
            "COMPARISON_CHAIN",
            "SYMMETRIC",
            importance
          )
        }
      }

      // === PRIORITY 3: IMPROVED BOUNDARY_CHECK ===
      val boundaryChecks = loop.ast.isControlStructure
        .filter(_.controlStructureType == "IF")
        .filterNot(_.inAst.isControlStructure.exists(_.eq(loop)))  // Not the loop condition itself
        .condition.code
        .filter(c =>
          (c.contains("<") || c.contains(">")) &&
          (c.contains("length") || c.contains("size") || c.contains("n"))
        )
        .l
      
      if (boundaryChecks.nonEmpty) {
        val importance = if (isMain) 0.8 else 0.6
        cesRecords += CESRecord(
          loopContext,
          "BOUNDARY",
          "BOUNDARY_CHECK",
          "guard",
          importance
        )
      }

      val inductionVars = loop.condition.ast.isIdentifier.name.l.toSet

      // === PATTERN: QUADRATIC_LIMIT ===
      val loopCondCode = loop.condition.code.mkString
      if (loopCondCode.contains("*") && 
         (loopCondCode.contains("<") || loopCondCode.contains(">") || loopCondCode.contains("!="))) {
        val importance = if (isMain) 1.0 else 0.8
        cesRecords += CESRecord(
          loopContext, 
          "LIMIT", 
          "QUADRATIC_LIMIT", 
          "COMPARE", 
          importance
        )
      }

      // === ASSIGNMENT PATTERNS ===
      val assignments =
        loop.ast
          .isCall
          .filter(c =>
            c.name == "<operator>.assignment" ||
            c.name == "<operator>.assignmentPlus" ||
            c.name == "<operator>.assignmentMinus" ||
            c.name == "<operator>.assignmentMultiplication" ||
            c.name == "<operator>.assignmentDivision"
          )
          .l
          
      // === C++ STL APPEND PATTERNS ===
      val containerAppends = 
        loop.ast
          .isCall
          .filter(c => CONTAINER_APPEND_OPS.contains(c.name))
          .l
          
      containerAppends.foreach { call =>
        val receiver = call.argument(0).code
        if (receiver.nonEmpty) {
          val importance = if (isMain) 1.0 else 0.8
          cesRecords += CESRecord(loopContext, receiver, "ACCUMULATIVE", "APPEND", importance)
        }
      }

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

          val isOptFlag = isOptimizationFlag(rawLhs)

          val isElementAccess = !isAccumulative && 
                                (rhs.contains("[") && rhs.contains("]")) ||
                                (assign.ast.isCall.exists(c => CONTAINER_ACCESS_OPS.contains(c.name)) && rhs.contains("]")) ||
                                (assign.ast.isCall.exists(c => CONTAINER_ACCESS_OPS.contains(c.name)))

          
          var importance = 0.0
          
          if (isOptFlag) {
            importance = 0.0
          } else if (isConditionalSwap || isNarrowingWindow) {
            importance = if (isMain) 1.0 else 0.8
          } else if (isAccumulative) {
            importance = if (isMain) 0.9 else 0.7
          } else if (controlGuarded && (guardCond.exists(c => isMaxUpdate(rawLhs, c)) || 
                                        guardCond.exists(c => isMinUpdate(rawLhs, c)))) {
            importance = if (isMain) 0.8 else 0.6
          } else if (isElementAccess) {
            importance = if (isMain) 0.6 else 0.4
          } else if (controlGuarded && !isOptFlag) {
            importance = if (isMain) 0.5 else 0.3
          } else {
            importance = if (isMain) 0.7 else 0.5
          }

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
            } else if (isElementAccess) {
              cesRecords += CESRecord(loopContext, lhs, "ELEMENT_ACCESS", "READ", importance)
            } else if (controlGuarded) {
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
}

// =======================================================
// PRIORITY 1+2: ENHANCED RECURSIVE CES
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>

    val name = method.name
    val calls = method.ast.isCall.l
    
    // PRIORITY 1 FIX 7: Improved recursion detection
    val recursive = calls.filter { call =>
      val callName = call.name
      callName == name ||
      callName.startsWith(name + "(") ||
      callName.endsWith("::" + name) ||
      callName.endsWith("." + name) ||
      callName.split("::").lastOption.contains(name) ||
      callName.split("\\.").lastOption.contains(name)
    }

    if (recursive.nonEmpty) {
      
      // PRIORITY 2 FIX 3: Detect tail recursion
      val paramNames = method.parameter.name.l.map(_.toLowerCase)
      
      val hasAccumulator = paramNames.exists(p =>
        p.contains("acc") ||
        p.contains("accumulator") ||
        p.contains("result") ||
        p.contains("sum") ||
        p.contains("total") ||
        p.contains("product") ||
        p.contains("count")
      )
      
      val isTailCall = method.ast.isReturn.exists { ret =>
        ret.ast.isCall.exists(c =>
          c.name == name &&
          ret.code.trim.startsWith("return " + name + "(")
        )
      }

      // PRIORITY 1 FIX 1: Enhanced accumulative detection
      val accumulative =
        // Method 1: Operator nodes
        calls.exists(c =>
          (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
          c.code.contains(name + "(")
        ) ||
        // Method 2: Check arguments of recursive calls
        recursive.exists { call =>
          val args = call.argument.code.l
          args.exists(arg =>
            (arg.contains("+") || arg.contains("*")) &&
            !arg.contains("++") &&
            !arg.contains("--")
          )
        } ||
        // Method 3: Check return statements with arithmetic
        method.ast.isReturn.exists { ret =>
          val retCode = ret.code
          (retCode.contains("+") || retCode.contains("*")) &&
          retCode.contains(name + "(")
        }

      // PRIORITY 3 FIX 9: Detect recursive binary search
      val hasMidpoint = method.ast.isIdentifier.name
        .exists(n => n == "mid" || n == "m" || n == "middle")
      
      val hasConditionalRecursion = method.ast.isControlStructure
        .exists(cs =>
          cs.controlStructureType == "IF" &&
          cs.ast.isCall.exists(_.name == name)
        )

      // PRIORITY 1 FIX 2: Normalized context
      val recContext = "rec_ANY"
      
      // Pattern classification
      if (hasMidpoint && hasConditionalRecursion) {
        // Recursive binary search
        cesRecords += CESRecord(recContext, "return", "RECURSIVE_BINARY_SEARCH", "NARROW", 1.0)
        
      } else if (hasAccumulator && isTailCall) {
        // Tail recursion with accumulator parameter
        cesRecords += CESRecord(recContext, "return", "TAIL_RECURSIVE", "ACCUMULATE", 1.0)
        
      } else if (accumulative && !isTailCall) {
        // Head recursion: computation happens on return
        cesRecords += CESRecord(recContext, "return", "HEAD_RECURSIVE", "ADD", 1.0)
        
      } else if (accumulative) {
        // Generic accumulative recursion
        cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
        
      } else {
        // Simple recursion without accumulation
        cesRecords += CESRecord(recContext, "return", "SIMPLE_RECURSIVE", "CALL", 0.9)
      }
    }
  }

// =======================================================
// PRIORITY 2 FIX 4: RECURSIVE HELPER DETECTION
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val name = method.name
    
    // Skip if already detected as directly recursive
    val isDirectlyRecursive = method.ast.isCall.exists(c =>
      c.name == name ||
      c.name.contains(name)
    )
    
    if (!isDirectlyRecursive) {
      // Get all non-operator methods this method calls
      val calledMethods = method.ast.isCall
        .name
        .filterNot(_.startsWith("<operator>"))
        .filterNot(_.startsWith("<"))
        .filterNot(_ == name)
        .toSet
      
      // Check if any called method is recursive
      val callsRecursiveHelper = calledMethods.exists { calledName =>
        cpg.method.name(calledName).exists { calledMethod =>
          calledMethod.ast.isCall.exists(c =>
            c.name == calledName ||
            c.name.contains(calledName)
          )
        }
      }
      
      if (callsRecursiveHelper) {
        cesRecords += CESRecord("rec_ANY", "return", "RECURSIVE_HELPER", "CALL", 0.9)
      }
    }
  }

// =======================================================
// PRIORITY 3 FIX 8: DIRECT_FORMULA PATTERN
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val hasLoops = method.controlStructure
      .exists(cs =>
        cs.controlStructureType == "FOR" ||
        cs.controlStructureType == "WHILE" ||
        cs.controlStructureType == "DO"
      )
    
    val isRecursive = method.ast.isCall.exists(_.name == method.name)
    
    // No loops, no recursion, has return with computation
    if (!hasLoops && !isRecursive) {
      val hasComputation = method.ast.isReturn.exists(ret =>
        ret.ast.isCall.exists(c =>
          c.name.contains("operator") ||
          c.name.contains("*") ||
          c.name.contains("+") ||
          c.name.contains("/")
        )
      )
      
      if (hasComputation) {
        cesRecords += CESRecord("direct", "return", "DIRECT_FORMULA", "COMPUTE", 0.8)
      }
    }
  }

// =======================================================
// PATTERN: SEQUENTIAL_ACCUMULATION
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method => 
    val assignments = method.ast.isCall.name("<operator>.assignment").l
    var multiAddCount = 0
    
    assignments.foreach { assign =>
        val rhs = assign.argument(2).code
        if (rhs.count(_ == '+') >= 2 && rhs.contains("[")) {
            multiAddCount += 1
        }
    }
    
    if (multiAddCount > 0) {
        cesRecords += CESRecord("seq_block", "var", "SEQUENTIAL_ACCUMULATION", "ADD", 0.8)
    }
  }

// =======================================================
// PRIORITY 2 FIX 6: ENHANCED STL ALGORITHM DETECTION
// =======================================================

// Map STL algorithms to CES patterns
val stlPatternMap = Map(
  // Accumulation algorithms
  "accumulate" -> ("ACCUMULATIVE", "ADD", 1.0),
  "reduce" -> ("ACCUMULATIVE", "ADD", 1.0),
  "count" -> ("ACCUMULATIVE", "ADD", 0.9),
  "count_if" -> ("ACCUMULATIVE", "ADD", 0.9),
  
  // Search algorithms
  "find" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "find_if" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "find_if_not" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "search" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 0.9),
  "binary_search" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  
  // Min/Max algorithms
  "max_element" -> ("MAX_UPDATE", "COMPARE", 1.0),
  "min_element" -> ("MIN_UPDATE", "COMPARE", 1.0),
  "minmax_element" -> ("MAX_UPDATE", "COMPARE", 0.9),
  
  // Sorting algorithms
  "sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "stable_sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "partial_sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 0.9),
  
  // Transformation algorithms
  "transform" -> ("RECOMPUTED", "ASSIGN", 0.8),
  "for_each" -> ("RECOMPUTED", "ASSIGN", 0.7),
  "copy" -> ("RECOMPUTED", "ASSIGN", 0.6),
  "fill" -> ("RECOMPUTED", "ASSIGN", 0.6)
)

// Detect STL algorithm calls
cpg.call
  .filter { c =>
    c.name.startsWith("std::") ||
    c.name.contains("::") ||
    stlPatternMap.keys.exists(algo => c.name.contains(algo))
  }
  .foreach { call =>
    // Extract algorithm name
    val algoName = if (call.name.contains("::")) {
      call.name.split("::").last
    } else {
      call.name
    }
    
    // Map to CES pattern
    stlPatternMap.get(algoName).foreach { case (evolution, operator, importance) =>
      cesRecords += CESRecord("stl_algo", "return", evolution, operator, importance)
    }
  }

// =======================================================
// OUTPUT JSON
// =======================================================
println(
  jsonArr(
    cesRecords.map { r =>
      jsonObj(Seq(
        "context"    -> jsonStr(r.context),
        "variable"   -> jsonStr(r.variable),
        "evolution"  -> jsonStr(r.evolution),
        "operator"   -> jsonStr(r.operator),
        "importance" -> r.importance.toString
      ))
    }.toSeq
  )
)
