# Auto-generated MCP wrappers
from fastmcp import FastMCP
from typing import List
from tooluniverse.execute_function import ToolUniverse

mcp = FastMCP('ToolUniverse MCP', stateless_http=True)
engine = ToolUniverse()
engine.load_tools()

@mcp.tool()
def get_active_ingredient_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_active_ingredient_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_dosage_and_storage_information_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_dosage_and_storage_information_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_abuse_info(
    abuse_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_abuse_info",
        "arguments": {
            "abuse_info": abuse_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_abuse_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_abuse_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_accessories(
    accessory_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_accessories",
        "arguments": {
            "accessory_name": accessory_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_accessories_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_accessories_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_active_ingredient(
    active_ingredient: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_active_ingredient",
        "arguments": {
            "active_ingredient": active_ingredient,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_active_ingredient_application_number_manufacturer_name_NDC_number_administration_route_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_active_ingredient_application_number_manufacturer_name_NDC_number_administration_route_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_application_number_manufacturer_name_NDC_number(
    application_manufacturer_or_NDC_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_application_number_manufacturer_name_NDC_number",
        "arguments": {
            "application_manufacturer_or_NDC_info": application_manufacturer_or_NDC_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_adverse_reaction(
    adverse_reaction: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_adverse_reaction",
        "arguments": {
            "adverse_reaction": adverse_reaction,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_adverse_reactions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_adverse_reactions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_alarm(
    alarm_type: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_alarm",
        "arguments": {
            "alarm_type": alarm_type,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_alarms_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_alarms_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_animal_pharmacology_info(
    pharmacology_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_animal_pharmacology_info",
        "arguments": {
            "pharmacology_info": pharmacology_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_animal_pharmacology_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_animal_pharmacology_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_info_on_conditions_for_doctor_consultation(
    condition: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_info_on_conditions_for_doctor_consultation",
        "arguments": {
            "condition": condition,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_info_on_conditions_for_doctor_consultation_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_info_on_conditions_for_doctor_consultation_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_info_on_consulting_doctor_pharmacist_for_drug_interactions(
    interaction_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_info_on_consulting_doctor_pharmacist_for_drug_interactions",
        "arguments": {
            "interaction_info": interaction_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_info_on_consulting_doctor_pharmacist_for_drug_interactions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_info_on_consulting_doctor_pharmacist_for_drug_interactions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_assembly_installation_info(
    field_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_assembly_installation_info",
        "arguments": {
            "field_info": field_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_assembly_installation_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_assembly_installation_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_boxed_warning(
    warning_text: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_boxed_warning",
        "arguments": {
            "warning_text": warning_text,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_boxed_warning_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_boxed_warning_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_calibration_instructions(
    calibration_instructions: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_calibration_instructions",
        "arguments": {
            "calibration_instructions": calibration_instructions,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_calibration_instructions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_calibration_instructions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_carcinogenic_mutagenic_fertility_impairment_info(
    carcinogenic_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_carcinogenic_mutagenic_fertility_impairment_info",
        "arguments": {
            "carcinogenic_info": carcinogenic_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_carcinogenic_mutagenic_fertility_impairment_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_carcinogenic_mutagenic_fertility_impairment_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_application_number_NUI_identifier_SPL_document_ID_SPL_set_ID(
    field_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_application_number_NUI_identifier_SPL_document_ID_SPL_set_ID",
        "arguments": {
            "field_info": field_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_clinical_pharmacology(
    clinical_pharmacology: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_clinical_pharmacology",
        "arguments": {
            "clinical_pharmacology": clinical_pharmacology,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_clinical_pharmacology_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_clinical_pharmacology_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_clinical_studies(
    clinical_studies: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_clinical_studies",
        "arguments": {
            "clinical_studies": clinical_studies,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_clinical_studies_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_clinical_studies_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_contraindications(
    contraindication_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_contraindications",
        "arguments": {
            "contraindication_info": contraindication_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_contraindications_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_contraindications_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_controlled_substance_DEA_schedule(
    controlled_substance_schedule: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_controlled_substance_DEA_schedule",
        "arguments": {
            "controlled_substance_schedule": controlled_substance_schedule,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_controlled_substance_DEA_schedule_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_controlled_substance_DEA_schedule_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_dependence_info(
    dependence_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_dependence_info",
        "arguments": {
            "dependence_info": dependence_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_dependence_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_dependence_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_disposal_info(
    disposal_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_disposal_info",
        "arguments": {
            "disposal_info": disposal_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_disposal_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_disposal_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_dosage_info(
    dosage_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_dosage_info",
        "arguments": {
            "dosage_info": dosage_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_dosage_forms_and_strengths_info(
    dosage_forms_and_strengths: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_dosage_forms_and_strengths_info",
        "arguments": {
            "dosage_forms_and_strengths": dosage_forms_and_strengths,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_dosage_forms_and_strengths_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_dosage_forms_and_strengths_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_abuse_types_and_related_adverse_reactions_and_controlled_substance_status(
    abuse_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_abuse_types_and_related_adverse_reactions_and_controlled_substance_status",
        "arguments": {
            "abuse_info": abuse_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_abuse_types_and_related_adverse_reactions_and_controlled_substance_status_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_abuse_types_and_related_adverse_reactions_and_controlled_substance_status_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_lab_test_interference(
    lab_test_interference: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_lab_test_interference",
        "arguments": {
            "lab_test_interference": lab_test_interference,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_lab_test_interference_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_lab_test_interference_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_drug_interactions(
    interaction_term: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_drug_interactions",
        "arguments": {
            "interaction_term": interaction_term,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_interactions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_interactions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_effective_time(
    effective_time: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_effective_time",
        "arguments": {
            "effective_time": effective_time,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_effective_time_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_effective_time_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_environmental_warning(
    environmental_warning: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_environmental_warning",
        "arguments": {
            "environmental_warning": environmental_warning,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_environmental_warning_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_environmental_warning_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_food_safety_warnings(
    field_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_food_safety_warnings",
        "arguments": {
            "field_info": field_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_general_precautions(
    precaution_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_general_precautions",
        "arguments": {
            "precaution_info": precaution_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_general_precautions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_general_precautions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_geriatric_use(
    geriatric_use: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_geriatric_use",
        "arguments": {
            "geriatric_use": geriatric_use,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_geriatric_use_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_geriatric_use_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_dear_health_care_provider_letter_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_dear_health_care_provider_letter_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_dear_health_care_provider_letter_info(
    letter_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_dear_health_care_provider_letter_info",
        "arguments": {
            "letter_info": letter_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_health_claim(
    health_claim: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_health_claim",
        "arguments": {
            "health_claim": health_claim,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_health_claims_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_health_claims_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_document_id(
    document_id: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_document_id",
        "arguments": {
            "document_id": document_id,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_document_id_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_document_id_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_inactive_ingredient(
    inactive_ingredient: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_inactive_ingredient",
        "arguments": {
            "inactive_ingredient": inactive_ingredient,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_inactive_ingredient_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_inactive_ingredient_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_indication(
    indication: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_indication",
        "arguments": {
            "indication": indication,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_indications_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_indications_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_information_for_owners_or_caregivers(
    field_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_information_for_owners_or_caregivers",
        "arguments": {
            "field_info": field_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_information_for_owners_or_caregivers_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_information_for_owners_or_caregivers_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_info_for_patients_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_info_for_patients_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_instructions_for_use(
    instructions_for_use: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_instructions_for_use",
        "arguments": {
            "instructions_for_use": instructions_for_use,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_instructions_for_use_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_instructions_for_use_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def retrieve_drug_name_by_device_use(
    intended_use_of_the_device: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "retrieve_drug_name_by_device_use",
        "arguments": {
            "intended_use_of_the_device": intended_use_of_the_device,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def retrieve_device_use_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "retrieve_device_use_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_child_safety_info(
    child_safety_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_child_safety_info",
        "arguments": {
            "child_safety_info": child_safety_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_child_safety_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_child_safety_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_labor_and_delivery_info(
    labor_and_delivery_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_labor_and_delivery_info",
        "arguments": {
            "labor_and_delivery_info": labor_and_delivery_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_labor_and_delivery_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_labor_and_delivery_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_lab_tests(
    lab_test_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_lab_tests",
        "arguments": {
            "lab_test_info": lab_test_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_lab_tests_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_lab_tests_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_mechanism_of_action_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_mechanism_of_action_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_mechanism_of_action(
    mechanism_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_mechanism_of_action",
        "arguments": {
            "mechanism_info": mechanism_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_microbiology(
    microbiology_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_microbiology",
        "arguments": {
            "microbiology_info": microbiology_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_microbiology_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_microbiology_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_nonclinical_toxicology_info(
    toxicology_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_nonclinical_toxicology_info",
        "arguments": {
            "toxicology_info": toxicology_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_nonclinical_toxicology_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_nonclinical_toxicology_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_nonteratogenic_effects(
    nonteratogenic_effects: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_nonteratogenic_effects",
        "arguments": {
            "nonteratogenic_effects": nonteratogenic_effects,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_nonteratogenic_effects_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_nonteratogenic_effects_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_info_for_nursing_mothers(
    nursing_mothers_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_info_for_nursing_mothers",
        "arguments": {
            "nursing_mothers_info": nursing_mothers_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_info_for_nursing_mothers_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_info_for_nursing_mothers_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_other_safety_info(
    safety_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_other_safety_info",
        "arguments": {
            "safety_info": safety_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_other_safety_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_other_safety_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_overdosage_info(
    overdosage_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_overdosage_info",
        "arguments": {
            "overdosage_info": overdosage_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_overdosage_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_overdosage_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_principal_display_panel(
    display_panel_content: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_principal_display_panel",
        "arguments": {
            "display_panel_content": display_panel_content,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_principal_display_panel_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_principal_display_panel_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def retrieve_drug_names_by_patient_medication_info(
    patient_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "retrieve_drug_names_by_patient_medication_info",
        "arguments": {
            "patient_info": patient_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def retrieve_patient_medication_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "retrieve_patient_medication_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_pediatric_use(
    pediatric_use_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_pediatric_use",
        "arguments": {
            "pediatric_use_info": pediatric_use_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pediatric_use_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pediatric_use_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_pharmacodynamics(
    pharmacodynamics: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_pharmacodynamics",
        "arguments": {
            "pharmacodynamics": pharmacodynamics,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pharmacodynamics_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pharmacodynamics_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_pharmacogenomics(
    pharmacogenomics: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_pharmacogenomics",
        "arguments": {
            "pharmacogenomics": pharmacogenomics,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pharmacogenomics_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pharmacogenomics_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_pharmacokinetics(
    pharmacokinetics_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_pharmacokinetics",
        "arguments": {
            "pharmacokinetics_info": pharmacokinetics_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pharmacokinetics_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pharmacokinetics_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_precautions(
    precautions: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_precautions",
        "arguments": {
            "precautions": precautions,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_precautions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_precautions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_pregnancy_effects_info(
    pregnancy_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_pregnancy_effects_info",
        "arguments": {
            "pregnancy_info": pregnancy_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pregnancy_effects_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pregnancy_effects_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_pregnancy_or_breastfeeding_info(
    pregnancy_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_pregnancy_or_breastfeeding_info",
        "arguments": {
            "pregnancy_info": pregnancy_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_pregnancy_or_breastfeeding_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_pregnancy_or_breastfeeding_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_contact_for_questions_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_contact_for_questions_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_recent_changes_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_recent_changes_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_reference(
    reference: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_reference",
        "arguments": {
            "reference": reference,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_reference_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_reference_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_residue_warning(
    residue_warning: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_residue_warning",
        "arguments": {
            "residue_warning": residue_warning,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_residue_warning_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_residue_warning_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_risk(
    risk_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_risk",
        "arguments": {
            "risk_info": risk_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_risk_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_risk_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_route(
    route: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_route",
        "arguments": {
            "route": route,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_route_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_route_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_safe_handling_warning(
    safe_handling_warning: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_safe_handling_warning",
        "arguments": {
            "safe_handling_warning": safe_handling_warning,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_safe_handling_warnings_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_safe_handling_warnings_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_set_id(
    set_id: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_set_id",
        "arguments": {
            "set_id": set_id,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_spl_indexing_data_elements(
    spl_indexing_data_elements: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_spl_indexing_data_elements",
        "arguments": {
            "spl_indexing_data_elements": spl_indexing_data_elements,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_spl_indexing_data_elements_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_spl_indexing_data_elements_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_medication_guide(
    medguide_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_medication_guide",
        "arguments": {
            "medguide_info": medguide_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_medication_guide_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_medication_guide_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_from_patient_package_insert(
    patient_package_insert: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_from_patient_package_insert",
        "arguments": {
            "patient_package_insert": patient_package_insert,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_patient_package_insert_from_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_patient_package_insert_from_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_ingredient(
    ingredient_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_ingredient",
        "arguments": {
            "ingredient_name": ingredient_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_ingredients_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_ingredients_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_spl_unclassified_section_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_spl_unclassified_section_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_stop_use_info(
    stop_use_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_stop_use_info",
        "arguments": {
            "stop_use_info": stop_use_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_stop_use_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_stop_use_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_storage_and_handling_info(
    storage_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_storage_and_handling_info",
        "arguments": {
            "storage_info": storage_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_storage_and_handling_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_storage_and_handling_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_safety_summary(
    summary_text: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_safety_summary",
        "arguments": {
            "summary_text": summary_text,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_safety_summary_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_safety_summary_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_teratogenic_effects(
    teratogenic_effects: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_teratogenic_effects",
        "arguments": {
            "teratogenic_effects": teratogenic_effects,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_teratogenic_effects_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_teratogenic_effects_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_population_use(
    population_use: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_population_use",
        "arguments": {
            "population_use": population_use,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_population_use_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_population_use_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_user_safety_warning_by_drug_names(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_user_safety_warning_by_drug_names",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_user_safety_warning(
    safety_warning: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_user_safety_warning",
        "arguments": {
            "safety_warning": safety_warning,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_name_by_warnings(
    warning_text: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_name_by_warnings",
        "arguments": {
            "warning_text": warning_text,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_warnings_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_warnings_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_warnings_and_cautions_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_warnings_and_cautions_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_names_by_warnings_and_cautions(
    warnings_and_cautions_info: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_names_by_warnings_and_cautions",
        "arguments": {
            "warnings_and_cautions_info": warnings_and_cautions_info,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_when_using_info(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_when_using_info",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_brand_name_generic_name(
    drug_name: str,
    limit: int
) -> dict:
    return engine.run_one_function({
        "name": "get_brand_name_generic_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit
        }
    })


@mcp.tool()
def get_do_not_use_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_do_not_use_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_purpose_info_by_drug_name(
    drug_name: str,
    limit: int,
    skip: int
) -> dict:
    return engine.run_one_function({
        "name": "get_purpose_info_by_drug_name",
        "arguments": {
            "drug_name": drug_name,
            "limit": limit,
            "skip": skip
        }
    })


@mcp.tool()
def get_drug_generic_name(
    drug_name: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_generic_name",
        "arguments": {
            "drug_name": drug_name
        }
    })


@mcp.tool()
def get_joint_associated_diseases_by_HPO_ID_list(
    HPO_ID_list: List[str],
    limit: int,
    offset: int
) -> dict:
    return engine.run_one_function({
        "name": "get_joint_associated_diseases_by_HPO_ID_list",
        "arguments": {
            "HPO_ID_list": HPO_ID_list,
            "limit": limit,
            "offset": offset
        }
    })


@mcp.tool()
def get_phenotype_by_HPO_ID(
    id: str
) -> dict:
    return engine.run_one_function({
        "name": "get_phenotype_by_HPO_ID",
        "arguments": {
            "id": id
        }
    })


@mcp.tool()
def get_HPO_ID_by_phenotype(
    query: str,
    limit: int,
    offset: int
) -> dict:
    return engine.run_one_function({
        "name": "get_HPO_ID_by_phenotype",
        "arguments": {
            "query": query,
            "limit": limit,
            "offset": offset
        }
    })


@mcp.tool()
def get_associated_targets_by_disease_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_targets_by_disease_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_associated_diseases_phenotypes_by_target_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_diseases_phenotypes_by_target_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def target_disease_evidence(
    efoId: str,
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "target_disease_evidence",
        "arguments": {
            "efoId": efoId,
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_drug_warnings_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_warnings_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_drug_mechanisms_of_action_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_mechanisms_of_action_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_associated_drugs_by_disease_efoId(
    efoId: str,
    size: int
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_drugs_by_disease_efoId",
        "arguments": {
            "efoId": efoId,
            "size": size
        }
    })


@mcp.tool()
def get_similar_entities_by_disease_efoId(
    efoId: str,
    threshold: float,
    size: int
) -> dict:
    return engine.run_one_function({
        "name": "get_similar_entities_by_disease_efoId",
        "arguments": {
            "efoId": efoId,
            "threshold": threshold,
            "size": size
        }
    })


@mcp.tool()
def get_similar_entities_by_drug_chemblId(
    chemblId: str,
    threshold: float,
    size: int
) -> dict:
    return engine.run_one_function({
        "name": "get_similar_entities_by_drug_chemblId",
        "arguments": {
            "chemblId": chemblId,
            "threshold": threshold,
            "size": size
        }
    })


@mcp.tool()
def get_similar_entities_by_target_ensemblID(
    ensemblId: str,
    threshold: float,
    size: int
) -> dict:
    return engine.run_one_function({
        "name": "get_similar_entities_by_target_ensemblID",
        "arguments": {
            "ensemblId": ensemblId,
            "threshold": threshold,
            "size": size
        }
    })


@mcp.tool()
def get_associated_phenotypes_by_disease_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_phenotypes_by_disease_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_drug_withdrawn_blackbox_status_by_chemblId(
    chemblId: List[str]
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_withdrawn_blackbox_status_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def search_category_counts_by_query_string(
    queryString: str
) -> dict:
    return engine.run_one_function({
        "name": "search_category_counts_by_query_string",
        "arguments": {
            "queryString": queryString
        }
    })


@mcp.tool()
def get_disease_id_description_by_name(
    diseaseName: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_id_description_by_name",
        "arguments": {
            "diseaseName": diseaseName
        }
    })


@mcp.tool()
def get_drug_id_description_by_name(
    drugName: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_id_description_by_name",
        "arguments": {
            "drugName": drugName
        }
    })


@mcp.tool()
def get_drug_indications_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_indications_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_target_gene_ontology_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_gene_ontology_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_homologues_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_homologues_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_safety_profile_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_safety_profile_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_biological_mouse_models_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_biological_mouse_models_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_genomic_location_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_genomic_location_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_subcellular_locations_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_subcellular_locations_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_synonyms_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_synonyms_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_tractability_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_tractability_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_classes_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_classes_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_enabling_packages_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_enabling_packages_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_target_interactions_by_ensemblID(
    ensemblId: str,
    page: dict
) -> dict:
    return engine.run_one_function({
        "name": "get_target_interactions_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId,
            "page": page
        }
    })


@mcp.tool()
def get_disease_ancestors_parents_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_ancestors_parents_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_disease_descendants_children_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_descendants_children_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_disease_locations_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_locations_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_disease_synonyms_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_synonyms_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_disease_description_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_description_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_disease_therapeutic_areas_by_efoId(
    efoId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_disease_therapeutic_areas_by_efoId",
        "arguments": {
            "efoId": efoId
        }
    })


@mcp.tool()
def get_drug_adverse_events_by_chemblId(
    chemblId: str,
    page: dict
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_adverse_events_by_chemblId",
        "arguments": {
            "chemblId": chemblId,
            "page": page
        }
    })


@mcp.tool()
def get_known_drugs_by_drug_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_known_drugs_by_drug_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_parent_child_molecules_by_drug_chembl_ID(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_parent_child_molecules_by_drug_chembl_ID",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_approved_indications_by_drug_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_approved_indications_by_drug_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_drug_description_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_description_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_drug_synonyms_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_synonyms_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_drug_trade_names_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_trade_names_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_drug_approval_status_by_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_drug_approval_status_by_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_chemical_probes_by_target_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_chemical_probes_by_target_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def drug_pharmacogenomics_data(
    chemblId: str,
    page: dict
) -> dict:
    return engine.run_one_function({
        "name": "drug_pharmacogenomics_data",
        "arguments": {
            "chemblId": chemblId,
            "page": page
        }
    })


@mcp.tool()
def get_associated_drugs_by_target_ensemblID(
    ensemblId: str,
    size: int,
    cursor: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_drugs_by_target_ensemblID",
        "arguments": {
            "ensemblId": ensemblId,
            "size": size,
            "cursor": cursor
        }
    })


@mcp.tool()
def get_associated_diseases_by_drug_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_diseases_by_drug_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def get_associated_targets_by_drug_chemblId(
    chemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_associated_targets_by_drug_chemblId",
        "arguments": {
            "chemblId": chemblId
        }
    })


@mcp.tool()
def multi_entity_search_by_query_string(
    queryString: str,
    entityNames: List[str],
    page: dict
) -> dict:
    return engine.run_one_function({
        "name": "multi_entity_search_by_query_string",
        "arguments": {
            "queryString": queryString,
            "entityNames": entityNames,
            "page": page
        }
    })


@mcp.tool()
def get_gene_ontology_terms_by_goID(
    goIds: List[str]
) -> dict:
    return engine.run_one_function({
        "name": "get_gene_ontology_terms_by_goID",
        "arguments": {
            "goIds": goIds
        }
    })


@mcp.tool()
def get_target_constraint_info_by_ensemblID(
    ensemblId: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_constraint_info_by_ensemblID",
        "arguments": {
            "ensemblId": ensemblId
        }
    })


@mcp.tool()
def get_publications_by_disease_efoId(
    entityId: str,
    additionalIds: List[str],
    startYear: int,
    startMonth: int,
    endYear: int,
    endMonth: int
) -> dict:
    return engine.run_one_function({
        "name": "get_publications_by_disease_efoId",
        "arguments": {
            "entityId": entityId,
            "additionalIds": additionalIds,
            "startYear": startYear,
            "startMonth": startMonth,
            "endYear": endYear,
            "endMonth": endMonth
        }
    })


@mcp.tool()
def get_publications_by_target_ensemblID(
    entityId: str,
    additionalIds: List[str],
    startYear: int,
    startMonth: int,
    endYear: int,
    endMonth: int
) -> dict:
    return engine.run_one_function({
        "name": "get_publications_by_target_ensemblID",
        "arguments": {
            "entityId": entityId,
            "additionalIds": additionalIds,
            "startYear": startYear,
            "startMonth": startMonth,
            "endYear": endYear,
            "endMonth": endMonth
        }
    })


@mcp.tool()
def get_publications_by_drug_chemblId(
    entityId: str,
    additionalIds: List[str],
    startYear: int,
    startMonth: int,
    endYear: int,
    endMonth: int
) -> dict:
    return engine.run_one_function({
        "name": "get_publications_by_drug_chemblId",
        "arguments": {
            "entityId": entityId,
            "additionalIds": additionalIds,
            "startYear": startYear,
            "startMonth": startMonth,
            "endYear": endYear,
            "endMonth": endMonth
        }
    })


@mcp.tool()
def get_target_id_description_by_name(
    targetName: str
) -> dict:
    return engine.run_one_function({
        "name": "get_target_id_description_by_name",
        "arguments": {
            "targetName": targetName
        }
    })


@mcp.tool()
def Finish() -> dict:
    return engine.run_one_function({
        "name": "Finish",
        "arguments": { }
    })


@mcp.tool()
def Tool_RAG(
    description: str,
    limit: int
) -> dict:
    return engine.run_one_function({
        "name": "Tool_RAG",
        "arguments": {
            "description": description,
            "limit": limit
        }
    })


@mcp.tool()
def CallAgent(
    solution: str
) -> dict:
    return engine.run_one_function({
        "name": "CallAgent",
        "arguments": {
            "solution": solution
        }
    })

def main():
    print("Starting ToolUniverse MCP server...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
