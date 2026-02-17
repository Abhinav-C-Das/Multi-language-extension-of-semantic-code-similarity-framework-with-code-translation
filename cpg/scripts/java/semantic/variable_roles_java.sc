import scala.collection.mutable
import scala.io.Source
import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language._

// =======================================================
// LOAD CPG
// =======================================================
importCpg("cpg.bin")

val targetFile =
  sys.env.getOrElse(
    "TARGET_FILE",
    throw new RuntimeException("TARGET_FILE not set")
  )

// Java CPG has empty filenames - use isExternal filter
val methods = cpg.method.filterNot(_.isExternal).l

// =======================================================
// LOAD CANONICALIZATION MAP
// =======================================================

def loadCanonicalMap(path: String): Map[String, String] = {
  val src = Source.fromFile(path).getLines().mkString
  val VarMap = "\"varMap\"\\s*:\\s*\\{([^}]*)\\}".r
  val Pair   = "\"([^\"]+)\"\\s*:\\s*\"([^\"]+)\"".r

  VarMap
    .findFirstMatchIn(src)
    .map { m =>
      Pair.findAllMatchIn(m.group(1))
        .map(p => p.group(1) -> p.group(2))
        .toMap
    }
    .getOrElse(Map.empty)
}

val canonPath =
  sys.env.getOrElse(
    "CANONICAL_JSON",
    throw new RuntimeException("CANONICAL_JSON not set")
  )

val canon =
  loadCanonicalMap(canonPath)

def canonVar(raw: String): String =
  canon.getOrElse(raw, raw)

// =======================================================
// DATA STRUCTURES
// =======================================================

val varUpdateKinds =
  mutable.Map[String, mutable.Set[String]]()

val roleCounts =
  mutable.Map(
    "LOOP_INDEX"   -> 0,
    "ACCUMULATOR"  -> 0,
    "MAX_TRACKER"  -> 0,
    "MIN_TRACKER"  -> 0,
    "FLAG"         -> 0,
    "TEMP"         -> 0
  )

// =======================================================
// HELPER FUNCTIONS
// =======================================================

def isAccumulator(assign: Call): Boolean =
  assign.name match {
    case "<operator>.assignmentPlus" |
         "<operator>.assignmentMinus" |
         "<operator>.assignmentMultiplication" =>
      true
    case "<operator>.assignment" =>
      val lhs = assign.argument(1).code
      val rhs = assign.argument(2).code
      rhs.contains(lhs)
    case _ => false
  }

def isMaxUpdate(assign: Call): Boolean =
  assign.astParent.isControlStructure &&
    assign.astParent.asInstanceOf[ControlStructure]
      .condition.code.mkString.contains(">")

def isMinUpdate(assign: Call): Boolean =
  assign.astParent.isControlStructure &&
    assign.astParent.asInstanceOf[ControlStructure]
      .condition.code.mkString.contains("<")

def isLoopIndex(v: String): Boolean =
  methods.exists { m =>
    m.controlStructure
      .filter(cs =>
        cs.controlStructureType == "FOR" ||
        cs.controlStructureType == "WHILE" ||
        cs.controlStructureType == "DO"
      )
      .exists { cs =>
        cs.condition.code.mkString.contains(v)
      }
  }

def isFlagVariable(v: String): Boolean =
  methods.exists { m =>
    m.assignment
      .filter(_.argument(1).code == v)
      .exists { a =>
        val rhs = a.argument(2).code
        rhs == "0" || rhs == "1"
      }
  }

// =======================================================
// COLLECT UPDATE PATTERNS PER VARIABLE
// =======================================================

methods.foreach { m =>
  m.ast
    .isCall
    .filter(_.name.startsWith("<operator>.assignment"))
    .foreach { assign =>

      val raw = assign.argument(1).code
      val v   = canonVar(raw)

      val kind =
        if (isAccumulator(assign)) "ACCUMULATIVE"
        else if (isMaxUpdate(assign)) "MAX_UPDATE"
        else if (isMinUpdate(assign)) "MIN_UPDATE"
        else "RECOMPUTED"

      val set =
        varUpdateKinds.getOrElseUpdate(v, mutable.Set())
      set += kind
    }
}

// =======================================================
// FEATURE 1: VARIABLE UPDATE HISTOGRAM
// =======================================================

val updateHistogram =
  mutable.Map(
    "ACCUMULATIVE" -> 0,
    "MAX_UPDATE"   -> 0,
    "MIN_UPDATE"   -> 0,
    "RECOMPUTED"   -> 0
  )

varUpdateKinds.foreach { case (_, kinds) =>
  kinds.foreach { k =>
    updateHistogram(k) += 1
  }
}

// =======================================================
// FEATURE 2: ACCUMULATOR VARIABLE COUNT
// =======================================================

val accumulatorVarCount =
  varUpdateKinds.count(_._2.contains("ACCUMULATIVE"))

// =======================================================
// FEATURE 3: ROLE-BASED VARIABLE CATEGORIES
// =======================================================

varUpdateKinds.keys.foreach { v =>
  if (isLoopIndex(v))
    roleCounts("LOOP_INDEX") += 1
  else if (varUpdateKinds(v).contains("ACCUMULATIVE"))
    roleCounts("ACCUMULATOR") += 1
  else if (varUpdateKinds(v).contains("MAX_UPDATE"))
    roleCounts("MAX_TRACKER") += 1
  else if (varUpdateKinds(v).contains("MIN_UPDATE"))
    roleCounts("MIN_TRACKER") += 1
  else if (isFlagVariable(v))
    roleCounts("FLAG") += 1
  else
    roleCounts("TEMP") += 1
}

// =======================================================
// OUTPUT JSON
// =======================================================

println("{")

updateHistogram.foreach { case (k, v) =>
  println(s"""  "var_update_$k": $v,""")
}

println(s"""  "accumulator_var_count": $accumulatorVarCount,""")

roleCounts.zipWithIndex.foreach { case ((k, v), i) =>
  val comma = if (i < roleCounts.size - 1) "," else ""
  println(s"""  "role_$k": $v$comma""")
}

println("}")
