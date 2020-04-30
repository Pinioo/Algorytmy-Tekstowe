import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout

def dfs(node, G, index = 0):
    if node is not None:
        node.index = index
        if node.parent is not None:
            if node.letter is not None:
                G.add_edge(node.parent.index, index, L=f"{node.letter}: {node.code().to01()}")
            else:
                G.add_edge(node.parent.index, index, L='')
        index += 1
        for v in [node.left, node.right]:
            index = dfs(v, G, index)
    return index

def draw_huff(trie_root):
    plt.figure(figsize=(30,40))
    G = nx.DiGraph()
    dfs(trie_root, G)
    
    pos = graphviz_layout(G, prog='dot')
        
    edge_labels = {(u,v): d['L'] for u,v,d in G.edges(data=True)} 
    
    nx.draw_networkx_edges(G, pos, with_labels=False, arrows=True)   
    nx.draw_networkx_edge_labels(G, pos, font_size=30, edge_labels=edge_labels)
    
    plt.show()