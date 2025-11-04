# pqueue.py


class PQueue:
    def __init__(self):
        self.queue = []
    
    def __get_children_indicies(self, i):
        left = i*2+1
        if left >= len(self.queue): left = None
        right = i*2+2
        if right >= len(self.queue): right = None
        return (left, right)
    
    def __get_parent_index(self, i):
        return (i-1)//2
    
    def __get_node_at_index(self, i):
        return self.queue[i] if i else None
    
    def get_root(self):
        if len(self.queue) == 0: return None
        return self.queue[0]
    
    def pop_node(self, node):
        current_index = self.queue.index(node)
        
        # if thing to pop is already at the end
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
                
            if right and right.score < self.queue[current_index].score:
                self.queue[current_index], self.queue[index_r] = self.queue[index_r], self.queue[current_index]
                current_index = index_r
                continue
            
            break
        return node

    def pop_index(self, index):
        if index >= len(self.queue): return None
        return self.pop_node(self.queue[index])

    def insert_node(self, node):
        self.queue.append(node)
        
        current_index = len(self.queue)-1
        while True:
            index_p = self.__get_parent_index(current_index)
            parent = self.__get_node_at_index(index_p)
            
            if parent and parent.score > self.queue[current_index].score:
                self.queue[current_index], self.queue[index_p] = self.queue[index_p], self.queue[current_index]
                current_index = index_p
                continue
            
            break

    def has_node(self, node):
        return node in self.queue
