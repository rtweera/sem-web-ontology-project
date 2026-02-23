# Competency Questions Summary

This document explains each competency question used to validate the ontology. Each question checks that core concepts and relationships can be retrieved with SPARQL.

## CQ1: Career Path Analysis

Checks that a career role is linked to the AI subfields it requires. This validates role-to-subfield relationships for career guidance.

## CQ2: Learning Resource Recommendations

Checks that learning resources are connected to a subfield and tagged with a level (e.g., intermediate). This validates topic-and-level recommendations.

## CQ3: Prerequisite Chain Discovery

Checks transitive prerequisites for an advanced topic like Deep Learning. This validates multi-step prerequisite links.

## CQ4: Tool Ecosystem Analysis

Checks that tools (e.g., frameworks) are labeled as open-source and mapped to the subfields that use them. This validates tool metadata and usage links.

## CQ5: Job Market Insights

Checks that roles include salary information and required skills. This validates salary data and skill requirements for high-paying roles.

## CQ6: Skill Gap Identification

Checks for missing skills when comparing a role (data scientist) to a specialization (Computer Vision). This validates difference queries over skill sets.

## CQ7: Expert Specialization Count

Checks that subfields are tagged with knowledge levels and can be counted by level. This validates categorization by proficiency tiers.

## CQ8: Topic Similarity Exploration

Checks topic-to-topic relationships (relatedness) and their associated tools. This validates semantic links across topics and tool usage.

## CQ9: Resource Type Distribution

Checks that resource types (books, courses, videos, papers) are modeled and mapped to subfields. This validates coverage by format.

## CQ10: Comprehensive Career Profile

Checks that a single query can join role, knowledge areas, skills, resources, and salary. This validates end-to-end data integration.
