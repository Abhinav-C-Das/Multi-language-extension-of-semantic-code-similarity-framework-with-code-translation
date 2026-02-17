importCpg("cpg.bin")

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable
import scala.io.Source
import java.io.File

// =======================================================
// CES V3 JAVA ENHANCED - MATCHING C++ CAPABILITIES
// 
// ENHANCEMENTS:
// 1. 5-Field Record Structure (context, variable, evolution, operator, importance)
// 2. Canonicalization Support
// 3. Advanced Pattern Detection (Guard, Swap, Min/Max, Boundary, Quadratic)
// 4. Container & Collection Support (List, Map, Set, Arrays)
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
// CES RECORD (Enhanced with variable field)
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
  "flag", "check", "visited", "seen", "updated", "temp"
)

// Java Collection Operations
val JAVA_COLLECTION_APPEND_OPS = Set("add", "put", "push", "offer", "append", "addElement")
val JAVA_COLLECTION_ACCESS_OPS = Set("get", "elementAt", "peek", "pop")

def isOptimizationFlag(varName: String): Boolean = {
  val lower = varName.toLowerCase
  OPTIMIZATION_FLAG_NAMES.exists(flag => lower.contains(flag))
}

// =======================================================
// ANALYSIS HELPERS
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
// MAIN METHOD DETECTION
// =======================================================
val mainMethodNames = Set("main", "arraySum", "binarySearch", "reverseString", "isPrime", 
                          "findMax", "findMin", "bubbleSort", "selectionSort", "factorial",
                          "fibonacci", "gcd", "lcm", "palindrome")

def isMainMethod(name: String): Boolean = 
  mainMethodNames.exists(m => name.toLowerCase.contains(m.toLowerCase))

// ==========================================================
// MULTI-FUNCTION LOOP ANALYSIS (ENHANCED)
// =======================================================
val allMethods = cpg.method.filter(!_.isExternal).l

allMethods.foreach { method =>
  val methodName = method.name
  val isMain = isMainMethod(methodName)
  val canonVars = canonIdMap.getOrElse(methodName, Map())
  
  method.controlStructure
    .filter(cs =>
      cs.controlStructureType == "FOR" ||
      cs.controlStructureType == "WHILE" ||
      cs.controlStructureType == "DO"
    )
    .foreach { loop =>
      
      val loopContext = "loop_ANY"
      
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

      // === PATTERN: COMPARISON_CHAIN (New) ===
      val comparisons = loop.ast.isCall
        .filter(c =>
          c.name.contains("equals") ||
          c.name == "<operator>.equals" ||
          c.name == "<operator>.notEquals"
        )
        .l

      for (comp <- comparisons) {
        val args = comp.argument.code.l
        
        val hasSymmetricAccess = 
          args.exists(a => a.contains("[i]") || a.contains("charAt(i)") || a.contains("get(i)")) &&
          args.exists(a => 
            a.contains("-i-1") || a.contains("-1-i") || 
            a.contains("- i - 1") ||
            (a.contains("len") && a.contains("-i")) ||
            (a.contains("length") && a.contains("-i")) ||
            (a.contains("size") && a.contains("-i"))
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

      // === PATTERN: BOUNDARY_CHECK (New) ===
      val boundaryChecks = loop.ast.isControlStructure
        .filter(_.controlStructureType == "IF")
        .filterNot(_.inAst.isControlStructure.exists(_.eq(loop)))
        .condition.code
        .filter(c =>
          (c.contains("<") || c.contains(">")) &&
          (c.contains("length") || c.contains("size") || c.contains("len"))
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

      // === PATTERN: QUADRATIC_LIMIT (New) ===
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

      // === JAVA CONTAINER APPENDS (New) ===
      val containerAppends = 
        loop.ast
          .isCall
          .filter(c => JAVA_COLLECTION_APPEND_OPS.exists(op => c.name.endsWith("." + op) || c.name == op))
          .l
          
      containerAppends.foreach { call =>
        // Try to get receiver object (e.g., list in list.add(x))
        val receiver = if (call.name.contains(".")) {
           try { call.astParent.code } catch { case _: Throwable => "collection" } 
        } else {
           "collection"
        }
        
        if (receiver.nonEmpty) {
          val importance = if (isMain) 1.0 else 0.8
          cesRecords += CESRecord(loopContext, receiver, "ACCUMULATIVE", "APPEND", importance)
        }
      }

      // === ASSIGNMENT PATTERNS ===
      val assignments =
        loop.ast
          .isCall
          .filter(c =>
            (c.name.contains("assignment") || c.name.contains("Assignment")) &&
            !c.name.contains("Increment") &&
            !c.name.contains("Decrement")
          )
          .l

      assignments.foreach { assign =>
        try {
          val args = assign.argument.l
          if (args.size >= 2) {
            val lhsNode = args(0)
            val rhsNode = args(1)
            
            val rawLhs = lhsNode.code
            val rhs = rhsNode.code
            val lhs = canonVars.getOrElse(rawLhs, rawLhs)
            
            if (!inductionVars.contains(rawLhs) && !isOptimizationFlag(rawLhs)) {
              
              val op =
                if (assign.name.contains("Plus")) "ADD"
                else if (assign.name.contains("Minus")) "SUB"
                else if (assign.name.contains("Multiplication")) "MUL"
                else if (assign.name.contains("Division")) "DIV"
                else "ASSIGN"
              
              val isAccumulative =
                rhs.contains(rawLhs) ||
                assign.name.contains("Plus") ||
                assign.name.contains("Minus") ||
                assign.name.contains("Multiplication") ||
                assign.name.contains("Division")
                
              val controlGuarded = isControlGuarded(assign, loop)
              val guardCond = getGuardCondition(assign, loop)

              // === NEW PATTERNS ===
              
              val isNarrowingWindow =
                !isAccumulative &&
                !controlGuarded &&
                (lhs == "v0" || lhs == "v1" || lhs == "high" || lhs == "low" || lhs == "right" || lhs == "left") &&
                (rhs.contains("mid") || rhs.contains("m") || 
                rhs.contains("+") || rhs.contains("-"))

              val isConditionalSwap =
                !isAccumulative &&
                !isNarrowingWindow &&
                controlGuarded &&
                guardCond.exists(c => 
                  c.contains(">") || c.contains("<") || 
                  c.contains("compareTo")
                ) &&
                (rawLhs == "temp" || rawLhs == "t" || rawLhs == "tmp" ||
                 rawLhs == "swap" || rawLhs == "tempVal")

              val isOptFlag = isOptimizationFlag(rawLhs)

              val isElementAccess = !isAccumulative && 
                                    (rhs.contains("[") && rhs.contains("]")) ||
                                    (assign.ast.isCall.exists(c => JAVA_COLLECTION_ACCESS_OPS.exists(op => c.name.contains(op))))

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
        } catch {
           case _: Throwable => // Skip problematic assignments
        }
      }
    }
}

// =======================================================
// ENHANCED RECURSIVE CES
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>

    val name = method.name
    val calls = method.ast.isCall.l
    
    // Improved recursion detection
    val recursive = calls.filter { call =>
      val callName = call.name
      callName == name ||
      callName.startsWith(name + "(") ||
      callName.endsWith("." + name) ||
      callName.split("\\.").lastOption.contains(name)
    }

    if (recursive.nonEmpty) {
      
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

      val accumulative =
        // Method 1: Check for operator nodes in return
        method.ast.isReturn.exists { ret =>
          val retCode = ret.code
          (retCode.contains("+") || retCode.contains("*")) &&
          retCode.contains(name + "(")
        } ||
        // Method 2: Check arguments of recursive calls for + or *
        recursive.exists { call =>
          val args = call.argument.code.l
          args.exists(arg =>
            (arg.contains("+") || arg.contains("*")) &&
            !arg.contains("++") &&
            !arg.contains("--")
          )
        } ||
        // Method 3: Check for arithmetic operators in method
        calls.exists(c =>
          (c.name == "<operator>.addition" || c.name == "<operator>.multiplication") &&
          c.code.contains(name + "(")
        )

      val hasMidpoint = method.ast.isIdentifier.name
        .exists(n => n == "mid" || n == "m" || n == "middle")
      
      val hasConditionalRecursion = method.ast.isControlStructure
        .exists(cs =>
          cs.controlStructureType == "IF" &&
          cs.ast.isCall.exists(_.name == name)
        )

      val recContext = "rec_ANY"
      
      if (hasMidpoint && hasConditionalRecursion) {
        cesRecords += CESRecord(recContext, "return", "RECURSIVE_BINARY_SEARCH", "NARROW", 1.0)
        
      } else if (hasAccumulator && isTailCall) {
        cesRecords += CESRecord(recContext, "return", "TAIL_RECURSIVE", "ACCUMULATE", 1.0)
        
      } else if (accumulative && !isTailCall) {
        cesRecords += CESRecord(recContext, "return", "HEAD_RECURSIVE", "ADD", 1.0)
        
      } else if (accumulative) {
        cesRecords += CESRecord(recContext, "return", "ACCUMULATIVE", "ADD", 1.0)
        
      } else {
        cesRecords += CESRecord(recContext, "return", "SIMPLE_RECURSIVE", "CALL", 0.9)
      }
    }
  }

// =======================================================
// DIRECT_FORMULA PATTERN
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
// RECURSIVE HELPER DETECTION
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method =>
    val name = method.name
    
    val isDirectlyRecursive = method.ast.isCall.exists(c =>
      c.name == name ||
      c.name.contains(name)
    )
    
    if (!isDirectlyRecursive) {
      val calledMethods = method.ast.isCall
        .name
        .filterNot(_.startsWith("<operator>"))
        .filterNot(_.startsWith("<"))
        .filterNot(_ == name)
        .toSet
      
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
// PATTERN: SEQUENTIAL_ACCUMULATION (New)
// =======================================================
cpg.method
  .filter(!_.isExternal)
  .foreach { method => 
    val assignments = method.ast.isCall.filter(_.name.contains("assignment")).l
    var multiAddCount = 0
    
    assignments.foreach { assign =>
        try {
           val rhs = assign.argument(1).code
           if (rhs.count(_ == '+') >= 2 && rhs.contains("[")) {
               multiAddCount += 1
           }
        } catch { case _: Throwable => }
    }
    
    if (multiAddCount > 0) {
        cesRecords += CESRecord("seq_block", "var", "SEQUENTIAL_ACCUMULATION", "ADD", 0.8)
    }
  }

// =======================================================
// JAVA COLLECTIONS/STREAMS API DETECTION
// =======================================================

// Map Java APIs to CES patterns
// Expanded with Arrays and Collections utils
val javaAPIPatternMap = Map(
  // Stream APIs - Accumulation
  "reduce" -> ("ACCUMULATIVE", "ADD", 1.0),
  "sum" -> ("ACCUMULATIVE", "ADD", 1.0),
  "count" -> ("ACCUMULATIVE", "ADD", 0.9),
  "average" -> ("ACCUMULATIVE", "ADD", 0.9),
  
  // Stream APIs - Search
  "findFirst" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "findAny" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "anyMatch" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 0.9),
  "allMatch" -> ("ACCUMULATIVE", "AND", 0.8),
  "noneMatch" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 0.8),
  
  // Stream APIs - Min/Max
  "max" -> ("MAX_UPDATE", "COMPARE", 1.0),
  "min" -> ("MIN_UPDATE", "COMPARE", 1.0),
  
  // Stream APIs - Transform
  "sorted" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "map" -> ("RECOMPUTED", "ASSIGN", 0.8),
  "filter" -> ("CONDITIONAL", "FILTER", 0.7),
  "forEach" -> ("RECOMPUTED", "ASSIGN", 0.6),
  "collect" -> ("ACCUMULATIVE", "COLLECT", 0.8),
  
  // Collections/Arrays APIs
  "sort" -> ("CONDITIONAL_SWAP", "ASSIGN", 1.0),
  "binarySearch" -> ("SEARCH_WITH_RETURN", "EARLY_EXIT", 1.0),
  "fill" -> ("RECOMPUTED", "ASSIGN", 0.6),
  "replaceAll" -> ("RECOMPUTED", "ASSIGN", 0.7)
)

// Detect Java API calls
cpg.call
  .filter { c =>
    c.name.contains(".stream") ||
    c.name.contains("Stream.") ||
    c.name.contains("Collections.") ||
    c.name.contains("Arrays.") ||
    c.name.contains("Math.") ||
    javaAPIPatternMap.keys.exists(api => c.name.contains(api))
  }
  .foreach { call =>
    // Extract method name
    val methodName = if (call.name.contains(".")) {
      call.name.split("\\.").last
    } else {
      call.name
    }
    
    // Map to CES pattern
    javaAPIPatternMap.get(methodName).foreach { case (evolution, operator, importance) =>
      cesRecords += CESRecord("java_api", "return", evolution, operator, importance)
    }
    
    // Check Math.max/min specifically
    if (call.name.contains("Math.max")) {
       cesRecords += CESRecord("java_api", "return", "MAX_UPDATE", "COMPARE", 1.0)
    } else if (call.name.contains("Math.min")) {
       cesRecords += CESRecord("java_api", "return", "MIN_UPDATE", "COMPARE", 1.0)
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
