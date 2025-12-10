# Data Model: Technical Book: Physical AI & Humanoid Robotics

**Purpose**: Defines the key entities and their relationships for the "Physical AI & Humanoid Robotics" technical book content. This model provides a structured view of the book's components, facilitating content creation, organization, and validation.

**Date**: 2025-12-10
**Spec**: specs/001-physical-ai-book/spec.md
**Plan**: specs/001-physical-ai-book/plan.md

---

## Entities

### Book

Represents the entire technical book.

*   **Attributes**:
    *   `Title` (String, e.g., "Physical AI & Humanoid Robotics")
    *   `Subtitle` (String, optional)
    *   `Version` (String, e.g., "1.0.0")
    *   `Author` (String, e.g., "AI Developer")
    *   `RatificationDate` (Date, ISO 8601, e.g., "YYYY-MM-DD")
    *   `LastAmendedDate` (Date, ISO 8601, e.g., "YYYY-MM-DD")
    *   `Description` (String, overview of the book's content and goals)
    *   `TargetAudience` (String, e.g., "Intermediate AI/ML, robotics, and software engineering students")
    *   `Toolchain` (String, e.g., "Docusaurus v3.9")
*   **Relationships**:
    *   Has many `Module`s.
    *   Has many `GlossaryTerm`s.

### Module

A logical grouping of related chapters, representing a major section of the book's curriculum.

*   **Attributes**:
    *   `ModuleID` (String, Unique identifier, e.g., "M1", "M2")
    *   `Title` (String, e.g., "ROS 2: Foundations & Humanoid Control")
    *   `Description` (String, overview of the module's learning objectives)
*   **Relationships**:
    *   Belongs to one `Book`.
    *   Has many `Chapter`s.

### Chapter

A self-contained unit of learning within a module, adhering to a predictable structure.

*   **Attributes**:
    *   `ChapterID` (String, Unique identifier, e.g., "M1-Ch1", "M2-Ch3")
    *   `Title` (String, e.g., "ROS 2: The Robotic Nervous System")
    *   `ModuleID` (String, foreign key to Module)
    *   `MinWordCount` (Integer, fixed at 1000, enforced by Constitution)
    *   `ActualWordCount` (Integer, calculated)
    *   `Status` (Enum: "Draft", "Review", "Approved", "Published")
    *   `Author(s)` (List of Strings)
*   **Relationships**:
    *   Belongs to one `Module`.
    *   Has one `ConceptExplanation` section.
    *   Has many `Diagram`s.
    *   Has many `CodeExample`s.
    *   Has one `AppliedExample` section.
    *   Has one `RealWorldInterpretation` section.
    *   Has many `Reference`s.

### Section

A distinct part within a chapter (e.g., Concept Explanation, Applied Example).

*   **Attributes**:
    *   `SectionID` (String, Unique identifier within Chapter, e.g., "Concept", "AppliedExample")
    *   `Title` (String, e.g., "Concept Explanation")
    *   `Content` (Markdown/MDX String)
*   **Relationships**:
    *   Belongs to one `Chapter`.

### CodeExample

A reproducible code snippet, script, or project file demonstrating a concept.

*   **Attributes**:
    *   `ExampleID` (String, Unique identifier, e.g., "M1-Ch1-Ex1")
    *   `ChapterID` (String, foreign key to Chapter)
    *   `FilePath` (String, relative path to `code/` directory)
    *   `Language` (String, e.g., "Python", "URDF", "YAML")
    *   `Dependencies` (List of Strings, e.g., "ROS 2 Galactic", "NVIDIA Isaac Sim 2023.1")
    *   `ExpectedOutput` (String, description or hash of expected output/behavior)
    *   `Description` (String, explanation of the example's purpose)
    *   `VerificationStatus` (Enum: "Untested", "Pass", "Fail", "Skipped")
*   **Relationships**:
    *   Belongs to one `Chapter`.

### Diagram

A visual representation that enhances understanding.

*   **Attributes**:
    *   `DiagramID` (String, Unique identifier, e.g., "M1-Ch1-Diag1")
    *   `ChapterID` (String, foreign key to Chapter)
    *   `FilePath` (String, relative path to `docs/assets/` directory)
    *   `Caption` (String)
    *   `Description` (String, alt text equivalent)
    *   `Type` (Enum: "Architecture", "Flowchart", "Kinematic", "UML", "Screenshot")
*   **Relationships**:
    *   Belongs to one `Chapter`.

### Reference

A formal citation to an external resource.

*   **Attributes**:
    *   `ReferenceID` (String, Unique identifier)
    *   `ChapterID` (String, foreign key to Chapter)
    *   `CitationFormat` (String, e.g., "IEEE", "APA", "URL")
    *   `CitationText` (String, full citation)
    *   `Link` (URL, optional)
    *   `Type` (Enum: "Official Documentation", "Peer-Reviewed Paper", "Vendor Manual", "Standard")
*   **Relationships**:
    *   Belongs to one `Chapter`.

### GlossaryTerm

A key robotics or technical term with its definition.

*   **Attributes**:
    *   `Term` (String, unique)
    *   `Definition` (String)
    *   `Context` (String, optional, e.g., "ROS 2", "VLA Systems")
*   **Relationships**:
    *   Belongs to one `Book`.

---

## Relationships Summary

*   `Book` has many `Module`s.
*   `Book` has many `GlossaryTerm`s.
*   `Module` has many `Chapter`s.
*   `Chapter` has one `ConceptExplanation` section.
*   `Chapter` has many `Diagram`s.
*   `Chapter` has many `CodeExample`s.
*   `Chapter` has one `AppliedExample` section.
*   `Chapter` has one `RealWorldInterpretation` section.
*   `Chapter` has many `Reference`s.
*   `Section`, `CodeExample`, `Diagram`, `Reference` each belong to one `Chapter`.
*   `GlossaryTerm` belongs to one `Book`.
