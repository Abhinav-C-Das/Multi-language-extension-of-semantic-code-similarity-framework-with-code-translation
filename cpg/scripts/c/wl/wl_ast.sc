importCpg("cpg.bin")

import io.shiftleft.semanticcpg.language._
import io.shiftleft.codepropertygraph.generated.nodes._
import scala.collection.mutable
import java.security.MessageDigest

// --------------------------------------------------
// REQUIRED: program scoping
// --------------------------------------------------
val targetFile =
  sys.env.getOrElse(
    "TARGET_FILE",
    throw new RuntimeException("TARGET_FILE not set")
  )

val methods =
  cpg.method.filter(m => m.filename.endsWith(targetFile)).l

// --------------------------------------------------
// Stable hash (deterministic)
// --------------------------------------------------
def stableHash(s: String): String = {
  val md = MessageDigest.getInstance("SHA-1")
  md.digest(s.getBytes("UTF-8"))
    .map("%02x".format(_))
    .mkString
}

// --------------------------------------------------
// Parameters
// --------------------------------------------------
val MAX_ITER = 2

// --------------------------------------------------
// WL feature histogram
// --------------------------------------------------
val featureCounts = mutable.Map[String, Int]()

def countLabel(iter: Int, label: String): Unit = {
  val key = s"wl_i${iter}_$label"
  featureCounts(key) = featureCounts.getOrElse(key, 0) + 1
}

// --------------------------------------------------
// WL per method (STRICTLY INTRA-PROGRAM)
// --------------------------------------------------
methods.foreach { m =>

  val nodes = m.ast.l

  // iteration 0 labels = AST node types
  var labels = mutable.Map[Long, String]()
  nodes.foreach { n =>
    labels(n.id) = n.label
    countLabel(0, n.label)
  }

  // WL iterations
  for (i <- 1 to MAX_ITER) {
    val newLabels = mutable.Map[Long, String]()

    nodes.foreach { n =>
      val childLabels =
        n.astChildren.l
          .map(c => labels.getOrElse(c.id, ""))
          .sorted
          .mkString(",")

      val combined = labels(n.id) + "|" + childLabels
      val hashed = stableHash(combined)

      newLabels(n.id) = hashed
      countLabel(i, hashed)
    }

    labels = newLabels
  }
}

// --------------------------------------------------
// OUTPUT JSON
// --------------------------------------------------
val json =
  featureCounts.toSeq
    .sortBy(_._1)
    .map { case (k, v) => s""""$k": $v""" }
    .mkString("{\n", ",\n", "\n}")

println(json)
