// =======================================================
// APM EXTRACTOR — CPG → Abstract Program Model JSON
//
// Walks a Joern CPG and produces a language-neutral JSON
// representation (APM) suitable for cross-language code
// generation.  Designed for CS-1 level programs.
//
// Usage:
//   joern --exit --cpg cpg.bin --script extract_apm.sc
//
// Environment:
//   TARGET_FILE (optional) — filter to a specific filename
// =======================================================

val cpgFile = sys.env.getOrElse("CPG_FILE", "cpg.bin")
importCpg(cpgFile)

import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._
import scala.collection.mutable

import scala.language.reflectiveCalls

// =======================================================
// CONFIGURATION
// =======================================================
val targetFileOpt: Option[String] = Option(System.getenv("TARGET_FILE"))

// =======================================================
// HELPERS — JSON output (no external deps)
// =======================================================
def jsonStr(s: String): String = {
  val escaped = s
    .replace("\\", "\\\\")
    .replace("\"", "\\\"")
    .replace("\n", "\\n")
    .replace("\r", "\\r")
    .replace("\t", "\\t")
  s""""$escaped""""
}

def indent(level: Int): String = "  " * level

// =======================================================
// TYPE CANONICALIZATION
// =======================================================
def canonicalizeType(rawType: String): String = {
  val t = rawType.trim.toLowerCase
    .replaceAll("\\s+", " ")
    .replaceAll("java\\.lang\\.", "")

  t match {
    case "int"                              => "INT"
    case "long" | "long int" | "long long"  => "LONG"
    case "long long int"                    => "LONG"
    case "double"                           => "DOUBLE"
    case "float"                            => "FLOAT"
    case "char"                             => "CHAR"
    case "bool" | "boolean" | "_bool"       => "BOOL"
    case "void"                             => "VOID"
    case s if s.contains("string")          => "STRING"
    case s if s.contains("int[]")           => "INT_ARRAY"
    case s if s.contains("int *")           => "INT_ARRAY"
    case s if s.contains("int*")            => "INT_ARRAY"
    case s if s.contains("long[]")          => "LONG_ARRAY"
    case s if s.contains("long long[]")     => "LONG_ARRAY"
    case s if s.contains("double[]")        => "DOUBLE_ARRAY"
    case s if s.contains("char[]")           => "CHAR_ARRAY"
    case s if s.contains("char *")           => "CHAR_ARRAY"
    case s if s.contains("char*")            => "CHAR_ARRAY"
    case s if s.contains("float[]")          => "FLOAT_ARRAY"
    case _                                   => "INT" // safe CS-1 default
  }
}

// Detect if a type is an array type
def isArrayType(rawType: String): Boolean = {
  val t = rawType.trim.toLowerCase
  t.contains("[]") || t.contains("*") || t.contains("int *")
}

// =======================================================
// DETECT SOURCE LANGUAGE
// =======================================================
def detectSourceLanguage(): String = {
  val filename = targetFileOpt.getOrElse("")
  if (filename.endsWith(".java"))     "java"
  else if (filename.endsWith(".cpp") ||
           filename.endsWith(".cc") ||
           filename.endsWith(".cxx")) "cpp"
  else if (filename.endsWith(".c"))   "c"
  else {
    // Heuristic: check if any method has "System.out" or "class" patterns
    val hasJavaIO = cpg.call.name(".*println.*").nonEmpty
    val hasPrintf = cpg.call.name("printf").nonEmpty
    val hasCout   = cpg.call.name(".*operator<<.*").nonEmpty
    if (hasJavaIO) "java"
    else if (hasCout) "cpp"
    else if (hasPrintf) "c"
    else "c" // default
  }
}

// =======================================================
// OPERATOR MAPPING
// =======================================================
val operatorMap = Map(
  "<operator>.addition"                -> "+",
  "<operator>.subtraction"             -> "-",
  "<operator>.multiplication"          -> "*",
  "<operator>.division"                -> "/",
  "<operator>.modulo"                  -> "%",
  "<operator>.lessThan"                -> "<",
  "<operator>.greaterThan"             -> ">",
  "<operator>.lessEqualsThan"          -> "<=",
  "<operator>.greaterEqualsThan"       -> ">=",
  "<operator>.equals"                  -> "==",
  "<operator>.notEquals"               -> "!=",
  "<operator>.logicalAnd"              -> "&&",
  "<operator>.logicalOr"               -> "||",
  "<operator>.logicalNot"              -> "!",
  "<operator>.not"                     -> "!",
  "<operator>.minus"                   -> "-",  // unary
  "<operator>.plus"                    -> "+",  // unary
  "<operator>.postIncrement"           -> "++",
  "<operator>.preIncrement"            -> "++",
  "<operator>.postDecrement"           -> "--",
  "<operator>.preDecrement"            -> "--"
)

val compoundAssignOps = Map(
  "<operator>.assignmentPlus"          -> "ADD",
  "<operator>.assignmentMinus"         -> "SUB",
  "<operator>.assignmentMultiplication"-> "MUL",
  "<operator>.assignmentDivision"      -> "DIV",
  "<operator>.assignmentModulo"        -> "MOD"
)

val unaryOps = Set(
  "<operator>.postIncrement", "<operator>.preIncrement",
  "<operator>.postDecrement", "<operator>.preDecrement",
  "<operator>.logicalNot", "<operator>.not",
  "<operator>.minus", "<operator>.plus"
)

val ioFunctions = Set(
  "printf", "puts", "fprintf", "scanf",
  "println", "print", "System.out.println", "System.out.print",
  "<operator>.formatString"
)

// =======================================================
// EXPRESSION TO JSON
// =======================================================
def exprToJson(node: AstNode, lvl: Int): String = {
  val I = indent(lvl)
  node match {

    // --- Identifier ---
    case id: Identifier =>
      s"""${I}{"kind": "IDENTIFIER", "name": ${jsonStr(id.name)}}"""

    // --- Literal ---
    case lit: Literal =>
      // Detect string literals by their code (starts with "), regardless of Joern's type
      val litType = if (lit.code.startsWith("\"")) {
        "STRING"
      } else if (lit.code.startsWith("'")) {
        "CHAR"
      } else {
        lit.typeFullName match {
          case t if t.toLowerCase.contains("int")    => "INT"
          case t if t.toLowerCase.contains("long")   => "INT"
          case t if t.toLowerCase.contains("double") ||
                    t.toLowerCase.contains("float") => "DOUBLE"
          case _                                     => "INT"
        }
      }
      s"""${I}{"kind": "LITERAL", "value": ${jsonStr(lit.code)}, "type": "$litType"}"""

    // --- Call (operators and function calls) ---
    case call: Call =>
      val name = call.name

      // Index access → ARRAY_ACCESS
      if (name == "<operator>.indexAccess" || name == "<operator>.indirectIndexAccess") {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val arrayExpr = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "IDENTIFIER", "name": "unknown"}"""
        val indexExpr = if (args.size > 1) exprToJson(args(1), lvl + 1) else s"""${I}  {"kind": "LITERAL", "value": "0", "type": "INT"}"""
        s"""${I}{
${I}  "kind": "ARRAY_ACCESS",
${I}  "array": 
${arrayExpr},
${I}  "index": 
${indexExpr}
${I}}"""
      }
      // Field access → MEMBER_ACCESS (e.g., arr.length)
      else if (name == "<operator>.fieldAccess" || name == "<operator>.memberAccess") {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val objExpr = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "IDENTIFIER", "name": "unknown"}"""
        val member = if (args.size > 1) args(1) match {
          case fi: FieldIdentifier => fi.canonicalName
          case id: Identifier      => id.name
          case other               => other.code
        } else "unknown"
        s"""${I}{
${I}  "kind": "MEMBER_ACCESS",
${I}  "object": 
${objExpr},
${I}  "member": ${jsonStr(member)}
${I}}"""
      }
      // Compound assignment → handled at statement level, but if reached as expr
      else if (compoundAssignOps.contains(name)) {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val target = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "IDENTIFIER", "name": "unknown"}"""
        val value  = if (args.size > 1) exprToJson(args(1), lvl + 1) else s"""${I}  {"kind": "LITERAL", "value": "0", "type": "INT"}"""
        s"""${I}{
${I}  "kind": "BINARY_OP",
${I}  "operator": ${jsonStr(operatorMap.getOrElse(name.replace("assignment", "").toLowerCase, "+"))},
${I}  "left": 
${target},
${I}  "right": 
${value}
${I}}"""
      }
      // Simple assignment as expr
      else if (name == "<operator>.assignment") {
        val args = call.argument.l.sortBy(_.argumentIndex)
        if (args.size > 1) exprToJson(args(1), lvl) // return the RHS value
        else s"""${I}{"kind": "LITERAL", "value": "0", "type": "INT"}"""
      }
      // Unary operators
      else if (unaryOps.contains(name)) {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val operand = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "IDENTIFIER", "name": "unknown"}"""
        val isPrefix = name.contains("pre") || name == "<operator>.logicalNot" || name == "<operator>.not" || name == "<operator>.minus" || name == "<operator>.plus"
        val opSymbol = operatorMap.getOrElse(name, "!")
        s"""${I}{
${I}  "kind": "UNARY_OP",
${I}  "operator": ${jsonStr(opSymbol)},
${I}  "operand": 
${operand},
${I}  "prefix": $isPrefix
${I}}"""
      }
      // Binary operators
      else if (operatorMap.contains(name)) {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val left  = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "LITERAL", "value": "0", "type": "INT"}"""
        val right = if (args.size > 1) exprToJson(args(1), lvl + 1) else s"""${I}  {"kind": "LITERAL", "value": "0", "type": "INT"}"""
        val op = operatorMap(name)
        s"""${I}{
${I}  "kind": "BINARY_OP",
${I}  "operator": ${jsonStr(op)},
${I}  "left": 
${left},
${I}  "right": 
${right}
${I}}"""
      }
      // Cast
      else if (name == "<operator>.cast") {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val targetType = canonicalizeType(call.typeFullName)
        val inner = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${I}  {"kind": "LITERAL", "value": "0", "type": "INT"}"""
        s"""${I}{
${I}  "kind": "CAST",
${I}  "target_type": "$targetType",
${I}  "expression": 
${inner}
${I}}"""
      }
      // Regular function call as expression
      else {
        val args = call.argument.l.sortBy(_.argumentIndex)
        // Filter out "this" argument for Java instance methods
        val realArgs = args.filter(a => a.argumentIndex > 0 || !a.code.startsWith("this"))
        val argJsons = realArgs.map(a => exprToJson(a, lvl + 2))
        s"""${I}{
${I}  "kind": "CALL_EXPR",
${I}  "function": ${jsonStr(cleanFuncName(name))},
${I}  "arguments": [
${argJsons.mkString(",\n")}
${I}  ]
${I}}"""
      }

    // --- FieldIdentifier (used in member access) ---
    case fi: FieldIdentifier =>
      s"""${I}{"kind": "IDENTIFIER", "name": ${jsonStr(fi.canonicalName)}}"""

    // --- fallback: use node code ---
    case other =>
      s"""${I}{"kind": "IDENTIFIER", "name": ${jsonStr(other.code.take(50))}}"""
  }
}

// Clean function name (remove package qualifiers for Java)
def cleanFuncName(name: String): String = {
  val cleaned = name.replaceAll("^.*\\.", "")
  cleaned
}

// =======================================================
// STATEMENT TO JSON
// =======================================================
def stmtToJson(node: AstNode, lvl: Int): Option[String] = {
  val I = indent(lvl)
  node match {

    // --- Local variable declaration ---
    case local: Local =>
      // Filter out C++ namespace leaks (e.g., Joern sees 'std' as a local)
      val skipNames = Set("std", "cout", "cin", "cerr", "endl")
      if (skipNames.contains(local.name)) None
      else {
        val cType = canonicalizeType(local.typeFullName)
        Some(s"""${I}{"kind": "DECLARE", "name": ${jsonStr(local.name)}, "type": "$cType"}""")
      }

    // --- Control structures ---
    case cs: ControlStructure =>
      cs.controlStructureType match {

        // --- FOR loop ---
        case "FOR" =>
          val children = cs.astChildren.l.sortBy { n =>
            try { 
                n match {
                    case withOrder: { def order: Int } => withOrder.order
                    case _ => n.order
                }
            } catch { case _: Throwable => 0 }
          }

          val stmtChildren = children.filterNot(_.isInstanceOf[Local])
          
          // FOR structure: init(order=1), condition(order=2), update(order=3), body(order=4)
          val initNode = stmtChildren.lift(0)
          val condNode = stmtChildren.lift(1)
          val updateNode = stmtChildren.lift(2)
          val bodyNode = stmtChildren.lift(3)

          val initJson = initNode match {
            case Some(c: Call) if c.name == "<operator>.assignment" =>
              val args = c.argument.l.sortBy(_.argumentIndex)
              val varName = if (args.nonEmpty) args.head.code else "i"
              val initVal = if (args.size > 1) exprToJson(args(1), lvl + 2) else s"""${indent(lvl+2)}{"kind": "LITERAL", "value": "0", "type": "INT"}"""
              // Check if there's a corresponding LOCAL node for the loop variable
              val loopVarType = cs.astChildren.collect { case l: Local => l }.headOption.map(_.typeFullName).getOrElse("int")
              s"""${I}  "var_init": {"kind": "DECLARE", "name": ${jsonStr(varName)}, "type": "${canonicalizeType(loopVarType)}", "init": \n${initVal}\n${I}  }"""
            case Some(other) =>
              s"""${I}  "var_init": {"kind": "EXPR_STMT", "expression": \n${exprToJson(other, lvl + 2)}\n${I}  }"""
            case None =>
              s"""${I}  "var_init": null"""
          }

          val condJson = condNode match {
            case Some(n) => s"""${I}  "condition": \n${exprToJson(n, lvl + 2)}"""
            case None    => s"""${I}  "condition": null"""
          }

          val updateJson = updateNode match {
            case Some(n) => s"""${I}  "update": \n${exprToJson(n, lvl + 2)}"""
            case None    => s"""${I}  "update": null"""
          }

          val bodyStmts = bodyNode match {
            case Some(b: Block) => b.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
            case Some(b)        => stmtToJson(b, lvl + 2).toList
            case None           => List.empty
          }
          val bodyJson = bodyStmts.mkString(",\n")

          Some(s"""${I}{
${I}  "kind": "FOR_LOOP",
${initJson},
${condJson},
${updateJson},
${I}  "body": [
${bodyJson}
${I}  ]
${I}}""")

        // --- WHILE loop ---
        case "WHILE" =>
          val condExpr = cs.condition.headOption
          val condJson = condExpr match {
            case Some(n) => exprToJson(n, lvl + 2)
            case None    => s"""${indent(lvl+2)}{"kind": "LITERAL", "value": "true", "type": "BOOL"}"""
          }
          val bodyBlock = cs.astChildren.collect { case b: Block => b }.headOption
          val bodyStmts = bodyBlock match {
            case Some(b) => b.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
            case None    => cs.astChildren.l.drop(1).flatMap(c => stmtToJson(c, lvl + 2))
          }
          val bodyJson = bodyStmts.mkString(",\n")

          Some(s"""${I}{
${I}  "kind": "WHILE_LOOP",
${I}  "condition": 
${condJson},
${I}  "body": [
${bodyJson}
${I}  ]
${I}}""")

        // --- DO-WHILE ---
        case "DO" =>
          val condExpr = cs.condition.headOption
          val condJson = condExpr match {
            case Some(n) => exprToJson(n, lvl + 2)
            case None    => s"""${indent(lvl+2)}{"kind": "LITERAL", "value": "true", "type": "BOOL"}"""
          }
          val bodyBlock = cs.astChildren.collect { case b: Block => b }.headOption
          val bodyStmts = bodyBlock match {
            case Some(b) => b.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
            case None    => List.empty
          }
          val bodyJson = bodyStmts.mkString(",\n")

          Some(s"""${I}{
${I}  "kind": "DO_WHILE",
${I}  "condition": 
${condJson},
${I}  "body": [
${bodyJson}
${I}  ]
${I}}""")

        // --- IF/ELSE ---
        case "IF" =>
          val condExpr = cs.condition.headOption
          val condJson = condExpr match {
            case Some(n) => exprToJson(n, lvl + 2)
            case None    => s"""${indent(lvl+2)}{"kind": "LITERAL", "value": "true", "type": "BOOL"}"""
          }

          val blocks = cs.astChildren.collect { case b: Block => b }.l
          val thenStmts = if (blocks.nonEmpty) {
            blocks.head.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
          } else {
            // Single statement if (no block)
            cs.astChildren.l.filter(!_.isInstanceOf[Block]).drop(1).take(1).flatMap(c => stmtToJson(c, lvl + 2))
          }
          val thenJson = thenStmts.mkString(",\n")

          val elseChildren = cs.astChildren.collect { case e: ControlStructure if e.controlStructureType == "ELSE" => e }.l
          val elseStmts = if (blocks.size > 1) {
            blocks(1).astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
          } else if (elseChildren.nonEmpty) {
            elseChildren.flatMap(e => e.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2)))
          } else {
            List.empty
          }

          val elseSection = if (elseStmts.nonEmpty) {
            s""",\n${I}  "else_body": [\n${elseStmts.mkString(",\n")}\n${I}  ]"""
          } else ""

          Some(s"""${I}{
${I}  "kind": "IF",
${I}  "condition": 
${condJson},
${I}  "then": [
${thenJson}
${I}  ]${elseSection}
${I}}""")

        // --- SWITCH, BREAK, CONTINUE ---
        case "BREAK"    => Some(s"""${I}{"kind": "BREAK"}""")
        case "CONTINUE" => Some(s"""${I}{"kind": "CONTINUE"}""")

        case _ => None
      }

    // --- Return statement ---
    case ret: Return =>
      val retExpr = ret.astChildren.l.headOption
      val valJson = retExpr match {
        case Some(n) => s""",\n${I}  "value": \n${exprToJson(n, lvl + 2)}"""
        case None    => ""
      }
      Some(s"""${I}{
${I}  "kind": "RETURN"${valJson}
${I}}""")

    // --- Call statements ---
    case call: Call =>
      val name = call.name

      // Compound assignment
      if (compoundAssignOps.contains(name)) {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val target = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${indent(lvl+1)}{"kind": "IDENTIFIER", "name": "unknown"}"""
        val value  = if (args.size > 1) exprToJson(args(1), lvl + 1) else s"""${indent(lvl+1)}{"kind": "LITERAL", "value": "0", "type": "INT"}"""
        val op = compoundAssignOps(name)
        Some(s"""${I}{
${I}  "kind": "COMPOUND_ASSIGN",
${I}  "target": 
${target},
${I}  "operator": "$op",
${I}  "value": 
${value}
${I}}""")
      }
      // Simple assignment
      else if (name == "<operator>.assignment") {
        val args = call.argument.l.sortBy(_.argumentIndex)
        val target = if (args.nonEmpty) exprToJson(args.head, lvl + 1) else s"""${indent(lvl+1)}{"kind": "IDENTIFIER", "name": "unknown"}"""
        val value  = if (args.size > 1) exprToJson(args(1), lvl + 1) else s"""${indent(lvl+1)}{"kind": "LITERAL", "value": "0", "type": "INT"}"""
        Some(s"""${I}{
${I}  "kind": "ASSIGN",
${I}  "target": 
${target},
${I}  "value": 
${value}
${I}}""")
      }
      // Print / I/O calls
      else if (isIOCall(name, call)) {
        val printInfo = buildPrintStmt(call, lvl)
        Some(printInfo)
      }
      // Regular function call
      else if (!name.startsWith("<operator>")) {
        val args = call.argument.l.sortBy(_.argumentIndex).filter(_.argumentIndex > 0)
        val argJsons = args.map(a => exprToJson(a, lvl + 2))
        Some(s"""${I}{
${I}  "kind": "CALL",
${I}  "function": ${jsonStr(cleanFuncName(name))},
${I}  "arguments": [
${argJsons.mkString(",\n")}
${I}  ]
${I}}""")
      }
      // Increment/decrement as statement
      else if (unaryOps.contains(name)) {
        val inner = exprToJson(call, lvl + 1)
        Some(s"""${I}{
${I}  "kind": "EXPR_STMT",
${I}  "expression": 
${inner}
${I}}""")
      }
      else {
        None // skip other operators that aren't statements
      }

    // --- Block ---
    case block: Block =>
      val stmts = block.astChildren.l.flatMap(c => stmtToJson(c, lvl + 1))
      if (stmts.nonEmpty) {
        Some(s"""${I}{
${I}  "kind": "BLOCK",
${I}  "body": [
${stmts.mkString(",\n")}
${I}  ]
${I}}""")
      } else None

    case _ => None
  }
}

// =======================================================
// I/O DETECTION AND NORMALIZATION
// =======================================================
def isIOCall(name: String, call: Call): Boolean = {
  name == "printf" || name == "puts" || name == "fprintf" ||
  name == "println" || name == "print" ||
  call.code.contains("System.out") ||
  call.code.contains("cout") ||
  name.contains("operator<<")
}

def buildPrintStmt(call: Call, lvl: Int): String = {
  val I = indent(lvl)
  
  // Flatten shiftLeft chains for C++ cout
  def flattenShiftLeft(c: Call): List[AstNode] = {
    val args = c.argument.l.sortBy(_.argumentIndex)
    if (args.size >= 2) {
      val left = args(0)
      val right = args(1)
      val leftArgs = left match {
        case childCall: Call if childCall.name == "<operator>.shiftLeft" => flattenShiftLeft(childCall)
        case _ => List(left)
      }
      leftArgs :+ right
    } else args
  }

  val args = if (call.name == "<operator>.shiftLeft" || call.name.contains("operator<<")) {
    flattenShiftLeft(call)
  } else {
    call.argument.l.sortBy(_.argumentIndex)
  }

  // Try to extract the content being printed
  val printArgs = if (call.name == "<operator>.shiftLeft" || call.name.contains("operator<<")) {
     args.filter(a => !a.code.contains("cout") && a.code != "std::endl" && a.code != "endl")
  } else {
     call.argument.l.sortBy(_.argumentIndex).filter(_.argumentIndex > 0)
  }

  val argJsons = printArgs.map(a => exprToJson(a, lvl + 2))

  // Try to figure out the format string
  val format = call.name match {
    case "printf" =>
      // First argument is the format string
      if (printArgs.nonEmpty) printArgs.head match {
        case lit: Literal => lit.code.replaceAll("^\"|\"$", "")
        case _ => "{}"
      } else "{}"
    case "println" | "System.out.println" | "puts" => 
      "{}\\n"
    case _ => 
      // For C++, if we filtered out endl, it must have a newline
      if (args.exists(a => a.code == "std::endl" || a.code == "endl")) "{}\\n"
      else "{}"
  }

  s"""${I}{
${I}  "kind": "PRINT",
${I}  "format": ${jsonStr(format)},
${I}  "arguments": [
${argJsons.mkString(",\n")}
${I}  ]
${I}}"""
}

// =======================================================
// PARAMETER ROLE DETECTION
// =======================================================
def detectParamRoles(method: Method, params: List[MethodParameterIn]): Map[String, String] = {
  val roles = mutable.Map[String, String]()

  // Find array params and potential size params
  val arrayParams = params.filter(p => isArrayType(p.typeFullName))
  val intParams   = params.filter(p => canonicalizeType(p.typeFullName) == "INT" && !isArrayType(p.typeFullName))

  // If there's an array and an int param, the int is likely ARRAY_SIZE
  if (arrayParams.nonEmpty && intParams.nonEmpty) {
    // Check if any int param is used in loop bounds
    val loopBounds = method.controlStructure
      .filter(cs => cs.controlStructureType == "FOR" || cs.controlStructureType == "WHILE")
      .flatMap(_.condition)
      .l

    for (ip <- intParams) {
      val nameLower = ip.name.toLowerCase
      val isCommonName = nameLower == "n" || nameLower == "size" || nameLower == "len" || nameLower == "length" || nameLower == "count"
      val usedInBound = loopBounds.exists(_.code.contains(ip.name))
      
      if (usedInBound || isCommonName) {
        roles(ip.name) = "ARRAY_SIZE"
      }
    }
  }

  // Mark remaining as DATA
  for (p <- params if !roles.contains(p.name)) {
    roles(p.name) = "DATA"
  }

  roles.toMap
}

// =======================================================
// METHOD EXTRACTION
// =======================================================
def extractMethod(method: Method, lvl: Int): String = {
  val I = indent(lvl)
  val name = method.name
  val retType = canonicalizeType(method.methodReturn.typeFullName)

  val params = method.parameter.l
    .filter(_.index > 0) // exclude "this" (index 0 in Java)
    .filter(p => !(method.name == "main" && p.name == "args")) // exclude Java main's String[] args
    .sortBy(_.index)

  val paramRoles = detectParamRoles(method, params)

  val paramJsons = params.map { p =>
    val pType = canonicalizeType(p.typeFullName)
    val role = paramRoles.getOrElse(p.name, "DATA")
    s"""${I}    {"name": ${jsonStr(p.name)}, "type": "$pType", "role": "$role"}"""
  }

  // Walk method body (the top-level block)
  val bodyBlock = method.block
  val bodyStmts = bodyBlock.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
  val bodyJson = bodyStmts.mkString(",\n")

  s"""${I}{
${I}  "name": ${jsonStr(name)},
${I}  "return_type": "$retType",
${I}  "parameters": [
${paramJsons.mkString(",\n")}
${I}  ],
${I}  "body": [
${bodyJson}
${I}  ]
${I}}"""
}

// =======================================================
// ENTRY POINT (main) EXTRACTION
// =======================================================
def extractEntryPoint(mainMethod: Option[Method], lvl: Int): String = {
  val I = indent(lvl)
  mainMethod match {
    case Some(m) =>
      val bodyStmts = m.block.astChildren.l.flatMap(c => stmtToJson(c, lvl + 2))
      val bodyJson = bodyStmts.mkString(",\n")
      s"""${I}{
${I}  "declarations": [],
${I}  "statements": [
${bodyJson}
${I}  ]
${I}}"""
    case None =>
      s"""${I}null"""
  }
}

// =======================================================
// MAIN: ASSEMBLE APM
// =======================================================

val srcLang   = detectSourceLanguage()
val srcFile   = targetFileOpt.getOrElse("unknown")

// Filter methods
val allMethods = cpg.method
  .filter(!_.isExternal)
  .filter(m => m.name != "<global>" && m.name != "<clinit>" && m.name != "<init>")
  .l

// Optionally filter by target file
val filteredMethods = targetFileOpt match {
  case Some(tf) =>
    val baseName = tf.replaceAll("\\.[^.]+$", "") // e.g. "MaxElement"
    val matched = allMethods.filter { m =>
      m.filename.endsWith(tf) ||
      m.filename.contains(tf) ||
      m.filename.endsWith(baseName) ||
      m.filename.toLowerCase.contains(baseName.toLowerCase)
    }
    // Fallback: if filter yields nothing (Java CPGs use synthetic filenames),
    // use ALL non-external methods. Safe because joern-parse was given a single file.
    if (matched.nonEmpty) matched else allMethods
  case None => allMethods
}

// Separate main from other functions
val mainMethod  = filteredMethods.find(_.name == "main")
val otherMethods = filteredMethods.filter(_.name != "main")

// Build function JSONs
val funcJsons = otherMethods.map(m => extractMethod(m, 2))

// Build entry point JSON
val entryJson = extractEntryPoint(mainMethod, 1)

// Assemble the full APM
val apmJson = s"""{
  "source_language": "$srcLang",
  "source_file": ${jsonStr(srcFile)},
  "functions": [
${funcJsons.mkString(",\n")}
  ],
  "entry_point": 
${entryJson}
}"""

println(apmJson)
