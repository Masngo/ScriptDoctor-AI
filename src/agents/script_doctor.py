import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from src.tools.parallel_mcp import ParallelSearchTool

class FactAssertion(BaseModel):
    line_number: int
    claim: str
    category: str = Field(description="HISTORICAL, MEDICAL, LEGAL_IP, or TECHNICAL")
    search_objective: str
    search_queries: List[str]

class ExtractedClaims(BaseModel):
    scene_location: str
    scene_time_period: str
    assertions: List[FactAssertion]

class AuditIssue(BaseModel):
    line_number: int
    claim: str
    severity: str = Field(description="HIGH, MEDIUM, or LOW")
    fact_check_verdict: str
    citations: List[str]
    suggested_rewrite: str

class ScriptAuditReport(BaseModel):
    scene_summary: str
    total_issues_found: int
    overall_risk_score: str
    audit_issues: List[AuditIssue]

class ScriptDoctorEngine:
    def __init__(self):
        self.client = genai.Client()
        self.parallel_tool = ParallelSearchTool()
        self.model_id = "gemini-3.5-flash"

    async def analyze_script_scene(self, script_text: str) -> ScriptAuditReport:
        extractor_prompt = f"""
        Extract factual, historical, medical, technical, or legal IP assertions from this screenplay.
        Formulate target search objectives for Parallel Search.
        
        SCREENPLAY:
        {script_text}
        """

        extraction_response = self.client.models.generate_content(
            model=self.model_id,
            contents=extractor_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedClaims,
                temperature=0.1
            )
        )
        
        extracted_data = ExtractedClaims.model_validate_json(extraction_response.text)

        grounding_data = []
        for assertion in extracted_data.assertions:
            search_result = await self.parallel_tool.execute_search(
                objective=assertion.search_objective,
                search_queries=assertion.search_queries
            )
            grounding_data.append({
                "line_number": assertion.line_number,
                "claim": assertion.claim,
                "category": assertion.category,
                "web_evidence": search_result
            })

        synthesis_prompt = f"""
        Synthesize the original script text with live ground-truth evidence provided by Parallel MCP.
        
        ORIGINAL SCRIPT:
        {script_text}
        
        PARALLEL WEB EVIDENCE:
        {json.dumps(grounding_data, indent=2)}
        
        Generate a line-by-line Script Coverage Audit with severity scores, citations, and screenwriter rewrites.
        """

        synthesis_response = self.client.models.generate_content(
            model=self.model_id,
            contents=synthesis_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ScriptAuditReport,
                temperature=0.2
            )
        )

        return ScriptAuditReport.model_validate_json(synthesis_response.text)
