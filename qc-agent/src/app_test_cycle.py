from memory import MemoryManager
# from agent.qcteam.team_2.orchestrator_agent import OrchestratorAgent
from agent.qcteam.team_3.orchestrator_agent import OrchestratorAgent
from agent.singletester import SingleQCAgent
from typing import List, Dict, Any, Set
from dotenv import load_dotenv
from utils import jira_client
import json
import asyncio
import traceback

load_dotenv()

import sys

def parse_chat_input(chat_input: str):
    """Parses the initial chat message to extract test case and cycle IDs."""
    parts = [p.strip() for p in chat_input.split(',')]
    output = {}
    for part in parts:
        if part.startswith('NCPP-T'):
            output['testCaseId'] = part
        elif part.startswith('NCPP-C'):
            output['testCycleId'] = part
    print(f"✅ Parsed Input: {output}")
    return output

def find_test_run_item_id(test_case_id: int, test_cycle_data: dict):
    """Finds the specific test run item ID to update."""
    # testRunItems = test_cycle_data.get("testRunItems", {})

    for item in test_cycle_data.get("testRunItems", {}).get("testRunItems", []):
        last_test_result = item.get('$lastTestResult', {})
        if last_test_result and last_test_result.get('testCase', {}).get('id') == test_case_id:
            return item['id']
    return None

def get_sort_key(item: Dict[str, Any]) -> float:
    try:
        name = item['$lastTestResult']['testCase']['name']
        # Split only on the first dot and check if the prefix is a digit
        parts = name.split('.', 1)
        if parts[0].isdigit():
            return float(parts[0])
    except (KeyError, IndexError, ValueError):
        pass # Ignore errors if keys or format are unexpected
    # Return infinity for items that can't be sorted numerically, placing them at the end
    return float('inf')

class TestProcessor:
    """
    Processes a test cycle to resolve preconditions and merge test steps.
    """
    def __init__(self, cycle_api_func, case_api_func):
        self._get_cycle_info = cycle_api_func
        self._get_case_info = case_api_func
        self.test_case_map = {}

    def _build_execution_order(
        self,
        test_case_key: str,
        ordered_test_cases: List[Dict[str, Any]],
        visited_keys: Set[str]
    ):
        """
        Recursively resolves preconditions and builds a flat list of test cases
        in the correct execution order.
        """
        # 1. Base case: If we have already processed this test case, stop to prevent cycles.
        if test_case_key in visited_keys:
            return

        # 2. Get the full test case data from our map.
        current_case = self.test_case_map.get(test_case_key)
        if not current_case:
            print(f"Warning: Test case with key '{test_case_key}' not found in the cycle. Skipping.")
            return

        # 3. Recursively process all preconditions first.
        precondition_str = current_case['$lastTestResult']['testCase'].get('precondition')
        if precondition_str:
            precondition_keys = [key.strip() for key in precondition_str.split(',')]
            for pre_key in precondition_keys:
                self._build_execution_order(pre_key, ordered_test_cases, visited_keys)

        # 4. After all its preconditions are in the list, add the current test case.
        ordered_test_cases.append(current_case)
        visited_keys.add(test_case_key)
    
    def _get_all_steps_for_test_case(self, test_case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetches and sorts the steps for a single test case.
        """
        test_case_id = test_case_data['$lastTestResult']['testCase']['id']
        info = self._get_case_info(test_case_id)
        
        try:
            steps = info['testScript']['stepByStepScript']['steps']
            # Sort steps by their 'index' to ensure correct order within the case
            steps.sort(key=lambda x: x.get('index', 0))
            return steps
        except (KeyError, TypeError):
            # Handle cases where steps might be missing
            return []

    async def process_test_cycle(self, test_cycle_id: int):
        """
        Main method to process a test cycle.
        """
        cycle_data = self._get_cycle_info(test_cycle_id)
        all_test_run_items = cycle_data.get('testRunItems', {}).get('testRunItems', [])

        all_test_run_items.sort(key=get_sort_key)

        # Create a map for quick lookup of test cases by their key
        self.test_case_map = {
            item['$lastTestResult']['testCase']['key']: item for item in all_test_run_items
        }

        # For each test case in the cycle, resolve its full step list
        for item in all_test_run_items:
            current_tc = item['$lastTestResult']['testCase']
            current_tc_key = current_tc['key']
            current_tc_name = current_tc['name']
            
            print(f"\n{'='*60}")
            print(f"Processing Test Case: {current_tc_key} - '{current_tc_name}'")
            print(f"{'-'*60}")

            # 1. Resolve the full execution order, including all preconditions
            ordered_test_cases_to_run = []
            visited_keys = set()
            self._build_execution_order(current_tc_key, ordered_test_cases_to_run, visited_keys)
            
            print("Execution Order (including preconditions):")
            for i, tc in enumerate(ordered_test_cases_to_run):
                print(f"  {i+1}. {tc['$lastTestResult']['testCase']['key']} - {tc['$lastTestResult']['testCase']['name']}")
            
            # 2. Get and merge all steps from the resolved test cases
            final_step_list = []
            for tc_data in ordered_test_cases_to_run:
                steps = self._get_all_steps_for_test_case(tc_data)
                final_step_list.extend(steps)

            # 3. Display the final merged list of steps
            print(f"\n>>> Final Merged List of {len(final_step_list)} Steps for {current_tc_key}:")
            if not final_step_list:
                print("  No steps found.")
            else:
                print(json.dumps(final_step_list, indent=2))
            print(f"{'='*60}")

            try:
                orchestrator = OrchestratorAgent()
                result = await orchestrator.run(final_step_list)
                print(f"\nWorkflow finished successfully for testcase {current_tc_name}.")

            except Exception as e:
                print(traceback.format_exc())


async def main():
    # The ID of the test cycle you want to process
    target_test_cycle_id = "NCPP-C203"
    
    # Instantiate the processor with the mock API functions
    processor = TestProcessor(
        cycle_api_func=jira_client.get_test_cycle_info,
        case_api_func=jira_client.get_test_case_info
    )
    
    # Run the process
    await processor.process_test_cycle(target_test_cycle_id)

asyncio.run(main())