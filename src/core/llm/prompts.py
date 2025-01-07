from langchain_core.prompts import ChatPromptTemplate


alias_prompt = ChatPromptTemplate.from_template("""
# Entity Resolution for Personal Names

Identify ALL variations that refer to the same person as the subject name, including those with titles/honorifics when combined with the name.

## Input
- Subject Name: [Person's name]
- Entity List: List of dictionaries with:
  - entity_type: Type of entity
  - entity_text: Name mention
  - context: Surrounding text

## Rules
1. Include variations with:
   - Full name matches
   - Partial name matches (first/last/middle)
   - Title/honorific + name combinations (e.g., "Chief Harrison", "Dr. Smith")
   - Name variations in contextually linked mentions


## Context Analysis
1. IMPORTANT: Scan entire context thoroughly for:
   - Role/position confirmations
   - Narrative continuity showing same person
   - References linking different name variations
2. Consider a match when:
   - Context shows same role/position
   - Actions/events link to subject
   - Clear reference to same individual

## Output Format
Return Python list of ALL valid name variations:
```python
# Valid: ["Mark Harrison", "Chief Harrison", "Chief Mark Harrison", "Harrison"]

```
"VERY IMPORTANTLY":
                                             
DO NOT make assumptions:
   - Similar names without clear linking context are not matches
   - Matching titles/roles alone are insufficient
   - Reject ambiguous or unclear references
Never include:
   - Standalone titles without names
   - Organizations
   - Generic references
   - Pronouns/descriptions   

THE ABOVE 2 POINTS ARE VERY IMPORATNT AND MAKE SURE OF THAT                                          
                                             

Subject: {subject}
Entity List: {final_result}
""")


s = """
You are an AI analyzer of entity relationships from given contexts. Given a subject and entity, determine if and how they are related based on the provided context.

Common relationship types: Family, Professional, Social, Legal, Government, Business

Common exact relationships examples:
- Family: Parent_of, Sibling_of, Spouse_of
- Professional: Manager_of, Employee_of, Colleague_of
- Legal: Lawyer_of, Judge_of
- Government: Advisor_to, Reports_to

Input format:
Subject: [name]
Entity: [name] 
Context: [text]

If no clear relationship is found in the context, return "NoRelationship".

The input will be provided in the following format:
Subject: [subject_name]
Entity: [entity_name]
Context:

[sentence_1]
[sentence_2]
[sentence_3]
...
"""


u = """
Subject: {{subject}}

Entity: {{entity}}

Context:
{{context_sentences}}

Analyze the relationship between the subject and the entity based on the provided context.
Provide the relationship_type and exact_relationship in your response.

Expected Output Values:
"relationship_type": "[Primary type of relationship]",
"exact_relationship": "[Specific relationship identifier]",
"explanation": "[Brief explanation of the relationship based on context]"
"""


relationship_entities_prompt = ChatPromptTemplate([("system", s), ("user", u)])
