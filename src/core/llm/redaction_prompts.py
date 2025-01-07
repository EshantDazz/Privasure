from langchain_core.prompts import ChatPromptTemplate

organisation_prompt = ChatPromptTemplate.from_template("""
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions an orgnisation:
The Orgnisation name and the context of the data will be mentioned in a way such that
"entity_text": This will contain the organization name 
"context": This will contain the corpus or the data which is present in the data


You need to check and verify if the data in the "context" is not related to the SUBJECT or the alias of the subjects. 
If the data is not related to the subject and related to some other Person then redact the exact text from context and tell me the part which should be redacted. 

IMPORTANT: When extracting text for redaction:
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "John works at Microsoft with [SUBJECT]", return only "John works at Microsoft"

Your role is to:
1. Send me the exact sentence or sequence of words which are related to some other person and with respect to that organisation
2. Look very carefully for sensitive data or security-related information that should be redacted
3. Always preserve any mentions of the SUBJECT or their aliases by excluding them from redacted segments

Important: Only redact information if it is related to a person who is not the SUBJECT. If the context doesn't explicitly connect information to a non-SUBJECT person, don't redact it.

Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject information]
Redaction_Reason: Concise explanation of why these specific segments need redaction


If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your ORGANIZATION json input:  
{input}                                                                                                                        
""")


persom_prompt = ChatPromptTemplate.from_template(""" 
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions a person:
The Person name and the context of the data will be mentioned in a way such that
"entity_text": This will contain the Person name 
"context": This will contain the corpus or the data which is present in the data


You need to:
1. Check and verify if the data in the "context" is not related to the SUBJECT or the alias of the subjects
2. Scan the entire context for ANY names of people (even if they're not in entity_text) who are not the SUBJECT or their aliases
3. For each name found (whether from entity_text or discovered in context), redact ONLY the specific portions about non-SUBJECT individuals
4. IMPORTANT: When extracting text for redaction:
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "John and [SUBJECT] went to school", only return "John" for redaction

Your role is to:
1. Send me the exact sentence or sequence of words which are related to any non-SUBJECT person
2. Look very carefully for sensitive data or security-related information that should be redacted
3. Ensure all names and associated information about non-SUBJECT individuals are identified and redacted
4. Always preserve any mentions of the SUBJECT or their aliases by excluding them from redacted segments

Important: Only redact information if it is related to a person who is not the SUBJECT. If the context doesn't explicitly connect information to a non-SUBJECT person, don't redact it.

Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject information]
Redaction_Reason: Concise explanation of why these specific segments need redaction


"IMPORTANT: Family Member Handling:
   - If the information relates to SUBJECT's family members (parents, siblings, spouse, children, etc.), DO NOT redact it
   - In such cases, return an empty list for Redacted_Text
   - In Redaction_Reason, specify which family member was detected (e.g., 'Information pertains to SUBJECT's mother')
   - Example: If text is 'His mother lives in New York', and it refers to SUBJECT's mother, return empty list"
If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your PERSON json input:  
{input}
""")


email_prompt = ChatPromptTemplate.from_template(""" 
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions an email:
The Email and the context of the data will be mentioned in a way such that
"entity_text": This will contain the Email address 
"context": This will contain the corpus or the data which is present in the data


You need to:
1. Check and verify if the data in the "context" is not related to the SUBJECT or the alias of the subjects
2. Scan the entire context for ANY email addresses not associated with the SUBJECT or their aliases
3. For each email found, redact ONLY the specific portions about non-SUBJECT individuals

IMPORTANT: When extracting text for redaction:
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "Contact john@email.com or [SUBJECT]", return only "Contact john@email.com"

Your role is to:
1. Send me the exact sentence or sequence of words which contain emails not belonging to the SUBJECT
2. Look very carefully for sensitive data or security-related information that should be redacted
3. Always preserve any mentions of the SUBJECT or their aliases by excluding them from redacted segments

Important: Only redact information if the email is not associated with the SUBJECT. If you cannot determine if an email belongs to the SUBJECT or not, do not redact it.

Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject information]
Redaction_Reason: Concise explanation of why these specific segments need redaction


If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your EMAIL json input:  
{input}
""")


phone_number_prompt = ChatPromptTemplate.from_template("""  
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions a phone number:
The Phone number and the context of the data will be mentioned in a way such that
"entity_text": This will contain the Phone number 
"context": This will contain the corpus or the data which is present in the data


You need to:
1. Check and verify if the data in the "context" is not related to the SUBJECT or the alias of the subjects
2. Scan the entire context for ANY phone numbers not associated with the SUBJECT or their aliases
3. For each phone number found, redact ONLY the specific portions about non-SUBJECT individuals

IMPORTANT: When extracting text for redaction:
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "Call 123-456-7890 or [SUBJECT]'s number", return only "Call 123-456-7890"

Your role is to:
1. Send me the exact sentence or sequence of words which contain phone numbers not belonging to the SUBJECT
2. Look very carefully for sensitive data or security-related information that should be redacted
3. Always preserve any mentions of the SUBJECT or their aliases by excluding them from redacted segments

Important: Only redact information if the phone number is not associated with the SUBJECT. If you cannot determine if a phone number belongs to the SUBJECT or not, do not redact it.

Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject information]
Redaction_Reason: Concise explanation of why these specific segments need redaction


If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your PHONE NUMBER json input:  
{input}
""")


address_prompt = ChatPromptTemplate.from_template(""" 
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions an address:
The Address and the context of the data will be mentioned in a way such that
"entity_text": This will contain the Address 
"context": This will contain the corpus or the data which is present in the data


You need to:
1. Check and verify if the data in the "context" is not related to the SUBJECT or the alias of the subjects
2. Scan the entire context for ANY addresses not associated with the SUBJECT or their aliases
3. For each address found, redact ONLY the specific portions about non-SUBJECT individuals

IMPORTANT: When extracting text for redaction:
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "John lives at 123 Oak Street while [SUBJECT] lives nearby", return only "John lives at 123 Oak Street"

                                                  
"IMPORTANT: Family Member Handling:
   - If the information relates to SUBJECT's family members (parents, siblings, spouse, children, etc.), DO NOT redact it
   - In such cases, return an empty list for Redacted_Text
   - In Redaction_Reason, specify which family member was detected (e.g., 'Information pertains to SUBJECT's mother')
   - Example: If text is 'His mother lives in New York', and it refers to SUBJECT's mother, return empty list"
                                                  
Your role is to:
1. Send me the exact sentence or sequence of words which contain addresses not belonging to the SUBJECT
2. Look very carefully for sensitive data or security-related information that should be redacted
3. Always preserve any mentions of the SUBJECT or their aliases by excluding them from redacted segments

Important: Only redact information if the address is not associated with the SUBJECT. If you cannot determine if an address belongs to the SUBJECT or not, do not redact it.

Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject information]
Redaction_Reason: Concise explanation of why these specific segments need redaction


If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your ADDRESS json input:  
{input}
 """)


pronoun_prompt = ChatPromptTemplate.from_template("""
Here is your "SUBJECT" and alias names of the "SUBJECT" {subjects}.
                                                     
I will be providing a dictionary which mentions pronouns:
The Pronoun and the context of the data will be mentioned in a way such that
"pos_cateogry": This will contain the category such as objective pronouns, gender pronouns, possesive pronouns etc  
"entity_text": This will contain the Pronoun 
"context": This will contain the corpus or the data which is present in the data

You need to check and verify if the pronouns in the "context" are not related to the SUBJECT or the alias of the subjects. 
Look within the context the pronoun I will be giving you in the entity text and the category in the pos_category and detect very carefully if they belong to subject or not

IMPORTANT: When extracting text for redaction:
   - Only redact if the pronoun clearly refers to someone other than the SUBJECT
   - Split sentences if needed to exclude SUBJECT mentions
   - Only include the minimum text necessary that contains non-SUBJECT information
   - Never include portions that mention the SUBJECT or their aliases
   - Example: If text is "He went to school with [SUBJECT]", return only "He went to school"

"IMPORTANT: Family Member Handling:
   - If the information relates to SUBJECT's family members (parents, siblings, spouse, children, etc.), DO NOT redact it
   - In such cases, return an empty list for Redacted_Text
   - In Redaction_Reason, specify which family member was detected (e.g., 'Information pertains to SUBJECT's mother')
   - Example: If text is 'His mother lives in New York', and it refers to SUBJECT's mother, return empty list"
                                                  
Go through all this and return me the following:
Redacted_Text: [list of minimal text segments containing ONLY non-subject pronoun information]
Redaction_Reason: Concise explanation of why these specific segments need redaction

If there is no data which should be redacted then just return an empty list in Redacted_Text   

Here is your PRONOUN json input:  
{input}
""")
