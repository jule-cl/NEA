# minheap.py

class Min_Heap:
    """
    A min heap priority queue where nodes are ordered by their score attribute.
    Each node's score is lower than both the scores of its children nodes, if they exist.
    Used by the autofill algorithm to always process the most constrained clue first.

    Variables:
        queue (list): The list of nodes stored in heap order.

    Methods:
        get_root: Returns the node with the lowest score without removing it.
        pop_node: Removes and returns a specific node from the heap.
        pop_index: Removes and returns the node at a given index.
        insert_node: Inserts a new node into the heap in the correct position.
        has_node: Returns whether a given node is in the heap.
        print_scores: Prints the scores of all nodes in the heap.
    """
    def __init__(self):
        """
        Initialises an empty min-heap.
        """
        self.queue = []
    
    def __get_children_indicies(self, i):
        """
        Returns the indices of the left and right children of the node at index i.
        Returns None for a child if it does not exist.

        Args:
            i (int): The index of the parent node.

        Returns:
            tuple[int or None, int or None]: The left and right child indices.
        """
        left = i*2+1
        if left >= len(self.queue): left = None
        right = i*2+2
        if right >= len(self.queue): right = None
        return (left, right)
    
    def __get_parent_index(self, i):
        """
        Returns the index of the parent of the node at index i.

        Args:
            i (int): The index of the child node.

        Returns:
            int: The index of the parent node.
        """
        return (i-1)//2
    
    def __get_node_at_index(self, i):
        """
        Returns the node at the given index, or None if the index is out of bounds.

        Args:
            i (int or None): The index to retrieve.

        Returns:
            CW_Clue or None: The node at the given index, or None if invalid.
        """
        return self.queue[i] if i!=None and 0<=i<=len(self.queue)-1 else None
    
    def get_root(self):
        """
        Returns the node with the lowest score without removing it.

        Returns:
            CW_Clue or None: The root node, or None if the heap is empty.
        """
        if len(self.queue) == 0: return None
        return self.queue[0]
    
    def pop_node(self, node):
        """
        Removes a specific node from the heap and restores the heap property.

        Args:
            node (CW_Clue): The node to remove. Must be present in the heap.

        Returns:
            CW_Clue: The removed node.
        """
        current_index = self.queue.index(node)
        
        # if node to pop is already at the end
        if current_index == len(self.queue)-1:
            return self.queue.pop()
        
        self.queue[current_index] = self.queue.pop()
        
        while True:
            index_l, index_r = self.__get_children_indicies(current_index)
            left, right = self.__get_node_at_index(index_l), self.__get_node_at_index(index_r)
            
            if left and left.score < self.queue[current_index].score:
                self.queue[current_index], self.queue[index_l] = self.queue[index_l], self.queue[current_index]
                current_index = index_l
                continue
                
            elif right and right.score < self.queue[current_index].score:
                self.queue[current_index], self.queue[index_r] = self.queue[index_r], self.queue[current_index]
                current_index = index_r
                continue
            
            break
        return node

    def pop_index(self, index):
        """
        Removes and returns the node at the given index in the heap.

        Args:
            index (int): The index of the node to remove.

        Returns:
            CW_Clue or None: The removed node, or None if the index is out of bounds.
        """
        if index >= len(self.queue): return None
        return self.pop_node(self.queue[index])

    def insert_node(self, node):
        """
        Inserts a new node into the heap and bubbles it up to restore the heap property.

        Args:
            node (CW_Clue): The node to insert.
        """
        self.queue.append(node)
        
        current_index = len(self.queue)-1
        while current_index != 0:
            index_p = self.__get_parent_index(current_index)
            parent = self.__get_node_at_index(index_p)
            
            if parent and (parent.score > self.queue[current_index].score):
                self.queue[current_index], self.queue[index_p] = self.queue[index_p], self.queue[current_index]
                current_index = index_p
                continue
            
            break

    def has_node(self, node):
        """
        Returns whether the given node is currently in the heap.

        Args:
            node (CW_Clue): The node to search for.

        Returns:
            bool: True if the node is in the heap, False otherwise.
        """
        return node in self.queue

    """Used for debugging"""
    def print_scores(self):
        """
        Prints the scores of all nodes in the heap to the console, separated by spaces.
        """
        print(' '.join([str(node.score) for node in self.queue]))
