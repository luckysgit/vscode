///////////////////////////////////////////////////////////////////////////////
// Neo4j Cypher Basics
// File: 01_cypher_basics.cypher
//
// This file demonstrates:
// 1. Cypher Syntax
// 2. Variables
// 3. Comments
// 4. RETURN Clause
// 5. Aliases (AS)
// 6. DISTINCT
// 7. LIMIT
// 8. SKIP
// 9. ORDER BY
///////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////
// SAMPLE DATA
///////////////////////////////////////////////////////////////////////////////

// Create some Person nodes

CREATE
    (alice:Person {name:'Alice', age:25}),
    (bob:Person {name:'Bob', age:30}),
    (charlie:Person {name:'Charlie', age:30}),
    (david:Person {name:'David', age:22}),
    (emma:Person {name:'Emma', age:40});


// Create Company nodes

CREATE
    (google:Company {name:'Google'}),
    (microsoft:Company {name:'Microsoft'});


// Create relationships

MATCH
    (alice:Person {name:'Alice'}),
    (bob:Person {name:'Bob'}),
    (charlie:Person {name:'Charlie'}),
    (google:Company {name:'Google'}),
    (microsoft:Company {name:'Microsoft'})

CREATE
    (alice)-[:WORKS_AT]->(google),
    (bob)-[:WORKS_AT]->(google),
    (charlie)-[:WORKS_AT]->(microsoft),
    (alice)-[:FRIEND]->(bob),
    (bob)-[:FRIEND]->(charlie);



///////////////////////////////////////////////////////////////////////////////
// 1. CYPHER SYNTAX
///////////////////////////////////////////////////////////////////////////////

//
// MATCH finds nodes and relationships.
//
// General Syntax:
//
// MATCH (node)-[relationship]->(anotherNode)
// RETURN node;
//


// Find all Person nodes

MATCH (p:Person)
RETURN p;



// Find all friendships

MATCH (a:Person)-[:FRIEND]->(b:Person)
RETURN a, b;



// Find employees and their companies

MATCH (p:Person)-[:WORKS_AT]->(c:Company)
RETURN p, c;



///////////////////////////////////////////////////////////////////////////////
// 2. VARIABLES
///////////////////////////////////////////////////////////////////////////////

//
// Variables are temporary names used within a query.
//
// (p:Person)
// p is the variable.
//
// Variables only exist while the query runs.
//


// Variable "person"

MATCH (person:Person)
RETURN person;



// Variable "employee"

MATCH (employee:Person)
RETURN employee;



// Variables for relationships

MATCH (a)-[r:FRIEND]->(b)
RETURN a, r, b;



// Access node properties using variables

MATCH (p:Person)
RETURN p.name, p.age;



///////////////////////////////////////////////////////////////////////////////
// 3. COMMENTS
///////////////////////////////////////////////////////////////////////////////

//
// Single-line comments use //
//


// This query returns every person

MATCH (p:Person)
RETURN p;



/*
Multi-line comments
can span
multiple lines.
*/

MATCH (p:Person)
RETURN p.name;



///////////////////////////////////////////////////////////////////////////////
// 4. RETURN CLAUSE
///////////////////////////////////////////////////////////////////////////////

//
// RETURN specifies what should be displayed.
//


// Return complete node

MATCH (p:Person)
RETURN p;



// Return one property

MATCH (p:Person)
RETURN p.name;



// Return multiple properties

MATCH (p:Person)
RETURN
    p.name,
    p.age;



// Return multiple variables

MATCH (p)-[:WORKS_AT]->(c)
RETURN
    p,
    c;



///////////////////////////////////////////////////////////////////////////////
// 5. ALIASES (AS)
///////////////////////////////////////////////////////////////////////////////

//
// AS renames output columns.
//


// Rename property

MATCH (p:Person)
RETURN
    p.name AS Name;



// Rename multiple columns

MATCH (p:Person)
RETURN
    p.name AS EmployeeName,
    p.age AS EmployeeAge;



// Rename calculated values

MATCH (p:Person)
RETURN
    p.name,
    p.age + 5 AS AgeAfterFiveYears;



///////////////////////////////////////////////////////////////////////////////
// 6. DISTINCT
///////////////////////////////////////////////////////////////////////////////

//
// DISTINCT removes duplicate rows.
//


// Without DISTINCT

MATCH (p)-[:WORKS_AT]->(c)
RETURN
    c.name;



// With DISTINCT

MATCH (p)-[:WORKS_AT]->(c)
RETURN DISTINCT
    c.name;



// DISTINCT on multiple columns

MATCH (p)-[:WORKS_AT]->(c)
RETURN DISTINCT
    p.name,
    c.name;



///////////////////////////////////////////////////////////////////////////////
// 7. LIMIT
///////////////////////////////////////////////////////////////////////////////

//
// LIMIT restricts the number of returned rows.
//


// Return first 2 persons

MATCH (p:Person)
RETURN
    p.name
LIMIT 2;



// Return first 3 persons

MATCH (p:Person)
RETURN
    p
LIMIT 3;



///////////////////////////////////////////////////////////////////////////////
// 8. SKIP
///////////////////////////////////////////////////////////////////////////////

//
// SKIP ignores the first N rows.
//


// Skip first two people

MATCH (p:Person)
RETURN
    p.name
SKIP 2;



// Pagination example

MATCH (p:Person)
RETURN
    p.name
SKIP 2
LIMIT 2;



///////////////////////////////////////////////////////////////////////////////
// 9. ORDER BY
///////////////////////////////////////////////////////////////////////////////

//
// ORDER BY sorts query results.
//


// Sort by name ascending

MATCH (p:Person)
RETURN
    p.name
ORDER BY p.name;



// Sort by name descending

MATCH (p:Person)
RETURN
    p.name
ORDER BY p.name DESC;



// Sort by age ascending

MATCH (p:Person)
RETURN
    p.name,
    p.age
ORDER BY p.age;



// Sort by age descending

MATCH (p:Person)
RETURN
    p.name,
    p.age
ORDER BY p.age DESC;



// Multiple sorting columns

MATCH (p:Person)
RETURN
    p.name,
    p.age
ORDER BY
    p.age DESC,
    p.name ASC;



///////////////////////////////////////////////////////////////////////////////
// COMBINING MULTIPLE CLAUSES
///////////////////////////////////////////////////////////////////////////////

//
// Execution Order:
//
// MATCH
// RETURN DISTINCT
// ORDER BY
// SKIP
// LIMIT
//

MATCH (p:Person)

RETURN DISTINCT
    p.name AS Name,
    p.age AS Age

ORDER BY Age DESC

SKIP 1

LIMIT 3;



///////////////////////////////////////////////////////////////////////////////
// PRACTICE QUERIES
///////////////////////////////////////////////////////////////////////////////

//
// Exercise 1
// Return all Person nodes.
//

MATCH (p:Person)
RETURN p;



//
// Exercise 2
// Return only names.
//

MATCH (p:Person)
RETURN p.name;



//
// Exercise 3
// Rename column.
//

MATCH (p:Person)
RETURN p.name AS EmployeeName;



//
// Exercise 4
// Return unique company names.
//

MATCH (p)-[:WORKS_AT]->(c)
RETURN DISTINCT c.name;



//
// Exercise 5
// Return first 5 people ordered by age.
//

MATCH (p:Person)
RETURN
    p.name,
    p.age
ORDER BY p.age
LIMIT 5;



//
// Exercise 6
// Skip first 2 people after sorting by name descending,
// then return the next 2.
//

MATCH (p:Person)
RETURN
    p.name
ORDER BY p.name DESC
SKIP 2
LIMIT 2;

///////////////////////////////////////////////////////////////////////////////
// END OF FILE
///////////////////////////////////////////////////////////////////////////////