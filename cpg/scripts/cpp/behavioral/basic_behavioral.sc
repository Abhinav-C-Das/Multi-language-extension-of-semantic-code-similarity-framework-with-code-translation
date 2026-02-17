import io.shiftleft.semanticcpg.language._

importCpg("cpg.bin")

val targetFile =
  sys.env.getOrElse("TARGET_FILE",
    throw new RuntimeException("TARGET_FILE not set"))

val methods =
  cpg.method.filter(m => m.filename.endsWith(targetFile)).l

val recursionFlag =
  if (methods.exists(m => m.call.exists(_.methodFullName == m.fullName))) 1 else 0

val iterativeFlag =
  if (methods.exists(_.controlStructure.exists(cs =>
    cs.controlStructureType match {
      case "FOR" | "WHILE" | "DO" | "FOREACH" => true
      case _                                  => false
    }
  ))) 1 else 0

val baseCaseFlag =
  if (recursionFlag == 1 &&
      methods.exists(_.controlStructure
        .filter(_.controlStructureType == "IF")
        .exists(_.ast.isReturn.nonEmpty)))
    1
  else 0

println("{")
println(s"""  "recursion_present": $recursionFlag,""")
println(s"""  "iterative_present": $iterativeFlag,""")
println(s"""  "base_case_present": $baseCaseFlag""")
println("}")

