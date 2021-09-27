# imports
from dice_ml.counterfactual_explanations import CounterfactualExplanations
import sys

obj = CounterfactualExplanations.from_json(sys.argv[1])
obj.visualize_as_list(show_only_changes=True)
