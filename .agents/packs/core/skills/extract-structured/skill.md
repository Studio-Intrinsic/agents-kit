---
id: extract-structured
name: Extract Structured
version: 1.0.0
description: |
  Pull structured data from unstructured content.
  Use to extract entities, relationships, or data from text, documents, or logs.
tags: [core, extraction]
inputs:
  - name: content
    type: string
    required: true
    description: The unstructured content to extract from
  - name: schema
    type: object
    required: false
    description: Target schema for extraction
outputs:
  - name: data
    type: object
    description: Extracted structured data
constraints:
  - Must only extract information present in source
  - Must handle missing fields gracefully
  - Must maintain fidelity to source
  - Must flag uncertain extractions
---

# Extract Structured

## Intent
Transform unstructured content into machine-readable structured data.

## Procedure
1. Understand the target schema/structure
2. Read through the source content
3. Identify relevant information
4. Map to target fields
5. Handle missing/ambiguous data
6. Validate extraction completeness
7. Flag confidence levels where uncertain

## Extraction Strategies
- **Entity extraction**: Names, dates, amounts, identifiers
- **Relationship extraction**: How entities relate
- **Event extraction**: What happened, when, who involved
- **Attribute extraction**: Properties of entities

## Confidence Handling
- **High**: Explicitly stated in source
- **Medium**: Implied or requires inference
- **Low**: Ambiguous, multiple interpretations possible
- **Missing**: Not present in source

## Failure Modes
- Hallucinating data not in source
- Missing data that is present
- Misinterpreting ambiguous content
- Forcing data into wrong schema

## Examples

### Input
Extract meeting details from this email:
"Hey team, let's sync on the Q2 roadmap tomorrow at 2pm in the large conf room. Bring your laptops. - Sarah"

### Output
```json
{
  "event": {
    "type": "meeting",
    "title": "Q2 Roadmap Sync",
    "confidence": "medium"
  },
  "datetime": {
    "relative": "tomorrow",
    "time": "14:00",
    "confidence": "high"
  },
  "location": {
    "name": "large conf room",
    "confidence": "high"
  },
  "organizer": {
    "name": "Sarah",
    "confidence": "high"
  },
  "attendees": {
    "value": "team",
    "confidence": "medium",
    "note": "specific members not listed"
  },
  "requirements": ["laptops"],
  "_missing": ["duration", "agenda", "dial-in"]
}
```
