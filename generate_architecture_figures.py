import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def draw_fig1():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    
    # Define boxes [x, y, w, h, label]
    boxes = [
        (1, 4, 3, 1, "Multi-Language\nSource Code\n(C/C++/Java)"),
        (5, 4, 3, 1, "Unified CPG\nParser\n(Joern)"),
        (9, 4, 3, 1, "Context Normalization\nProtocol"),
        (6, 6, 3, 1, "Abstract Program\nModel (APM)"),
        (6, 2, 3, 1, "Semantic Code\nSimilarity Evaluation")
    ]
    
    for (x, y, w, h, label) in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, linewidth=2, edgecolor='black', facecolor='lightblue', boxstyle="round,pad=0.3")
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, horizontalalignment='center', verticalalignment='center', fontsize=12, fontweight='bold')
        
    # Arrows
    ax.annotate('', xy=(5, 4.5), xytext=(4, 4.5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate('', xy=(9, 4.5), xytext=(8, 4.5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate('', xy=(7.5, 6), xytext=(7.5, 5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate('', xy=(7.5, 3), xytext=(7.5, 4), arrowprops=dict(arrowstyle="<-", lw=2))
    
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    plt.title("Figure 1: Extended Framework Architecture Pipeline", fontsize=16)
    plt.tight_layout()
    os.makedirs('docs/unw1/IEEE_Access_Draft', exist_ok=True)
    plt.savefig('docs/unw1/IEEE_Access_Draft/fig1.png', dpi=300)
    plt.savefig('docs/unw1/fig1.png', dpi=300)
    plt.close()

def draw_fig3():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    
    boxes = [
        (1, 2, 2.5, 1, "Code Property\nGraph (CPG)"),
        (4.5, 2, 3, 1, "APM JSON\nIntermediate Rep."),
        (8.5, 3, 2, 1, "C++ Emitter"),
        (8.5, 1, 2, 1, "Java Emitter")
    ]
    
    for (x, y, w, h, label) in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, linewidth=2, edgecolor='black', facecolor='lightgreen', boxstyle="round,pad=0.3")
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, horizontalalignment='center', verticalalignment='center', fontsize=11, fontweight='bold')

    # Arrows
    ax.annotate('', xy=(4.5, 2.5), xytext=(3.5, 2.5), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate('', xy=(8.5, 3.5), xytext=(7.5, 2.7), arrowprops=dict(arrowstyle="->", lw=2, connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    ax.annotate('', xy=(8.5, 1.5), xytext=(7.5, 2.3), arrowprops=dict(arrowstyle="->", lw=2, connectionstyle="angle,angleA=0,angleB=-90,rad=10"))
    
    ax.text(4, 2.7, "Extract", ha="center")
    ax.text(8, 3.3, "Generate", ha="center")
    
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    plt.title("Figure 3: Preliminary APM Translation Pipeline", fontsize=14)
    plt.tight_layout()
    plt.savefig('docs/unw1/IEEE_Access_Draft/fig3.png', dpi=300)
    plt.savefig('docs/unw1/fig3.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    draw_fig1()
    draw_fig3()
    print("Successfully generated fig1.png and fig3.png")
