def max_depth(node, the_tree):
    if node == -1:
        return 0

    left_depth = max_depth(the_tree.children_left[node], the_tree) + 1
    right_depth = max_depth(the_tree.children_right[node], the_tree) + 1

    return max(left_depth, right_depth)
