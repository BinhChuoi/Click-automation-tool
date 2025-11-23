


def test_extract_filename_dot_notation():
    scenario = {"condition": "Z_.image == 'field' and Z_.mask == 'mask'"}
    names = ContextActionExecutor.extract_filename_from_condition(scenario)
    assert "Z_.image" in names
    assert "Z_.mask" in names
    assert "Z_" not in names


def test_extract_filename_exclude_builtins_and_keywords():
    scenario = {"condition": "any([k in detected_objects for k in ['field.png']]) and for and if"}
    names = ContextActionExecutor.extract_filename_from_condition(scenario)
    # Should not include Python keywords, eval globals, or temp variables like k
    assert "any" not in names
    assert "for" not in names
    assert "if" not in names
    assert "detected_objects" not in names
    assert "k" not in names
    assert "field.png" in names


def test_extract_filename_complex():
    scenario = {"condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'hole.png']]) and not ('rhubard_seed_tool.png' in detected_objects['default'])"}
    names = ContextActionExecutor.extract_filename_from_condition(scenario)
    # Should not include temp variable k, built-ins, or keywords
    assert "k" not in names
    assert "detected_objects" not in names
    assert "all" not in names
    assert "default" not in names

import pytest
from common.utils.context_action_executor import ContextActionExecutor

def test_all_in_default_branch():
    scenario = {"condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'hole.png']])"}
    detected_objects = {"default": ['base_template.png', 'hole.png', 'other.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True

def test_any_in_default_branch():
    scenario = {"condition": "any([k in detected_objects['default'] for k in ['sunflower_crop_v2.png', 'rhubard_crop.png']])"}
    detected_objects = {"default": ['base_template.png', 'sunflower_crop_v2.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True

def test_all_in_basket_window():
    scenario = {"condition": "all([k in detected_objects['default'] for k in ['basket_window.png', 'close_button.png']])"}
    detected_objects = {"default": ['basket_window.png', 'close_button.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True

def test_not_in_detected_objects():
    scenario = {"condition": "all([k in detected_objects['default'] for k in ['base_template.png', 'basket_v2.png']]) and not ('rhubard_seed_tool.png' in detected_objects['default'])"}
    detected_objects = {"default": ['base_template.png', 'basket_v2.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True
    detected_objects = {"default": ['base_template.png', 'basket_v2.png', 'rhubard_seed_tool.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is False

def test_captcha_passer_any():
    scenario = {"condition": "any([(k in detected_objects['captcha_passer']) for k in ['goblin', 'chest', 'skeleton']])"}
    detected_objects = {"captcha_passer": ['goblin', 'other']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True
    detected_objects = {"captcha_passer": ['other']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is False

def test_detect_captcha_any():
    scenario = {"condition": "any([(k in detected_objects['default']) for k in ['attempt_left_blue.png', 'tap_chest.png', 'attempt_left_red.png']])"}
    detected_objects = {"default": ['attempt_left_blue.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True
    detected_objects = {"default": ['other.png']}
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is False
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is False


def test_dot_notation_variable_extraction():
    scenario = {"condition": "Z_.image == 'field' and Z_.mask == 'mask'"}
    filenames = ContextActionExecutor.extract_filename_from_condition(scenario)
    assert "Z_.image" in filenames
    assert "Z_.mask" in filenames
    assert "Z_" not in filenames  # Only dot notation extracted

def test_dot_notation_in_detected_objects():
    scenario = {"condition": "'field' in detected_objects['images']"}
    detected_objects = {"images": ["field", "mask"]}
    # Should evaluate True since Z_.image == 'field' and 'field' in images
    assert ContextActionExecutor.evaluate_scenario_condition(scenario, detected_objects) is True
