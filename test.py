import random
from collections import defaultdict

class AutoFill:
    def __init__(self, grid, word_list):
        """
        grid: 2D list where None = black, '' = empty white
        word_list: list of words
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        
        # Organize words by length for O(1) lookup
        self.words_by_length = defaultdict(list)
        for word in word_list:
            word = word.upper().strip()
            if word:
                self.words_by_length[len(word)].append(word)
        
        # Find all slots
        self.slots = self._find_slots()
        
        # Track which words we've used
        self.used_words = set()
        
        # Cache for pattern matching
        self.pattern_cache = {}
    
    def _find_slots(self):
        """Find all horizontal and vertical word slots"""
        slots = []
        
        # Horizontal slots
        for row in range(self.rows):
            col = 0
            while col < self.cols:
                if self.grid[row][col] is not None:  # Not black
                    start = col
                    while col < self.cols and self.grid[row][col] is not None:
                        col += 1
                    
                    length = col - start
                    if length >= 2:  # Only 2+ letter words
                        slots.append({
                            'row': row,
                            'col': start,
                            'length': length,
                            'dir': 'H',
                            'cells': [(row, start + i) for i in range(length)]
                        })
                else:
                    col += 1
        
        # Vertical slots
        for col in range(self.cols):
            row = 0
            while row < self.rows:
                if self.grid[row][col] is not None:
                    start = row
                    while row < self.rows and self.grid[row][col] is not None:
                        row += 1
                    
                    length = row - start
                    if length >= 2:
                        slots.append({
                            'row': start,
                            'col': col,
                            'length': length,
                            'dir': 'V',
                            'cells': [(start + i, col) for i in range(length)]
                        })
                else:
                    row += 1
        
        return slots
    
    def fill(self, allow_reuse=False, max_attempts=1):
        """
        Fill the grid with words
        allow_reuse: Can the same word appear multiple times?
        max_attempts: Try multiple times with different orderings
        """
        self.allow_reuse = allow_reuse
        
        for attempt in range(max_attempts):
            # Clear grid
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.grid[row][col] is not None:
                        self.grid[row][col] = ''
            
            self.used_words.clear()
            self.pattern_cache.clear()
            
            # Sort slots by constraint (most constrained first)
            # This is KEY for performance
            ordered_slots = self._order_slots()
            
            if self._backtrack(ordered_slots, 0):
                return True
            
            # Shuffle for next attempt
            random.shuffle(self.slots)
        
        return False
    
    def _order_slots(self):
        """Order slots by difficulty (most constrained first)"""
        # Calculate how many possible words each slot has
        slot_scores = []
        for slot in self.slots:
            pattern = self._get_pattern(slot)
            possible = self._get_matching_words(slot['length'], pattern)
            slot_scores.append((len(possible), slot))
        
        # Sort by fewest options (most constrained first)
        slot_scores.sort(key=lambda x: x[0])
        return [slot for _, slot in slot_scores]
    
    def _backtrack(self, ordered_slots, slot_idx):
        """Recursive backtracking"""
        # Success!
        if slot_idx >= len(ordered_slots):
            return True
        
        slot = ordered_slots[slot_idx]
        pattern = self._get_pattern(slot)
        
        # Get possible words for this slot
        candidates = self._get_matching_words(slot['length'], pattern)
        
        # No valid words - fail fast
        if not candidates:
            return False
        
        # Limit candidates to speed up (try most common first)
        # You can add word frequency scoring here
        candidates = candidates[:50]  # Try top 50
        random.shuffle(candidates)  # Randomize for variety
        
        # Try each candidate
        for word in candidates:
            if not self.allow_reuse and word in self.used_words:
                continue
            
            # Place word
            self._place_word(slot, word)
            
            if not self.allow_reuse:
                self.used_words.add(word)
            
            # Recurse
            if self._backtrack(ordered_slots, slot_idx + 1):
                return True
            
            # Backtrack
            self._remove_word(slot)
            if not self.allow_reuse:
                self.used_words.remove(word)
        
        return False
    
    def _get_pattern(self, slot):
        """Get current pattern (e.g., 'C_T' for partially filled slot)"""
        pattern = []
        for r, c in slot['cells']:
            char = self.grid[r][c]
            pattern.append(char if char else '.')
        return ''.join(pattern)
    
    def _get_matching_words(self, length, pattern):
        """Get words matching length and pattern"""
        # Use cache for repeated patterns
        cache_key = (length, pattern)
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]
        
        candidates = self.words_by_length.get(length, [])
        
        # If no pattern constraints, return all
        if '.' not in pattern:
            # Pattern is fully specified - exact match only
            result = [pattern] if pattern in candidates else []
        else:
            # Filter by pattern
            result = [w for w in candidates if self._matches_pattern(w, pattern)]
        
        self.pattern_cache[cache_key] = result
        return result
    
    def _matches_pattern(self, word, pattern):
        """Check if word matches pattern (. = wildcard)"""
        if len(word) != len(pattern):
            return False
        
        for w_char, p_char in zip(word, pattern):
            if p_char != '.' and p_char != w_char:
                return False
        
        return True
    
    def _place_word(self, slot, word):
        """Place word in grid"""
        for i, (r, c) in enumerate(slot['cells']):
            self.grid[r][c] = word[i]
    
    def _remove_word(self, slot):
        """Remove word from grid (only clear if not crossing)"""
        for r, c in slot['cells']:
            # Only clear if no other slot has filled this cell
            if not self._has_crossing(r, c, slot):
                self.grid[r][c] = ''
    
    def _has_crossing(self, row, col, current_slot):
        """Check if cell has a crossing word from another slot"""
        for slot in self.slots:
            if slot == current_slot:
                continue
            
            if (row, col) in slot['cells']:
                # Check if this slot has a letter here
                pattern = self._get_pattern(slot)
                idx = slot['cells'].index((row, col))
                if pattern[idx] != '.':
                    return True
        
        return False
    
# Load words
with open('words_alpha.txt', 'r') as f:
    word_list = [line.strip() for line in f if 2 <= len(line.strip()) <= 15]

# Create grid (None = black square, '' = empty)
grid = [
    ['', '', '', ''],
    ['', '', '', ''],
    ['', '', '', ''],
    ['', '', '', '']
]

# Fill it
autofill = AutoFill(grid, word_list)
success = autofill.fill(allow_reuse=False, max_attempts=3)

if success:
    print("Filled successfully!")
    for row in grid:
        print(' '.join(cell if cell else '?' for cell in row))
else:
    print("Could not fill grid")