Here are 5 simple, focused prompts similar to your "top students" example that test basic query functionality with clear visualization needs:

### 1. Basic Top-N Query

*"Show top 5 students by CGPA with their names and grades"*

*"Show the 3 youngest students with their names and ages"*
- Tests: `ORDER BY` with `LIMIT`, text + number display
- Expected Viz: Simple table (no natural chart mapping)

### 2. Filtered Top-N 
*"List the 5 female students with highest CGPA"*
- Tests: `WHERE` + `ORDER BY` combination
- Expected Viz: Bar chart (names vs CGPA)

### 3. Bottom-N Identification  
*"Show 10 students with lowest CGPA and their enrollment years"*
- Tests: Ascending sort, multiple field display
- Expected Viz: Red-themed bar chart (negative emphasis)

### 4. Threshold-Based Top  
*"List all students with CGPA above 9.0 and their email addresses"*
- Tests: Filtering without sorting
- Expected Viz: Table (email text makes charts impractical)

### 5. Grouped Top  
*"Show the top student by CGPA from each grade level"*
- Tests: `GROUP BY` with ranking
- Expected Viz: Grouped bar chart (grade vs CGPA)

### Why These Work Well:
1. **Clear Intent** - Each has unambiguous success criteria
2. **Simple Structure** - Focus on 1-2 database operations
3. **Natural Visualizations** - Either obvious chart type or clear table need
4. **Progressive Complexity** - Builds from basic to grouped queries



Would you like me to provide the expected SQL for any of these?