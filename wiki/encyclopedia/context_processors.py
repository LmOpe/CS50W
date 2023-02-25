from . import util
import random

# Creating context_processors
def add_variable_to_context(request):
    return {
        'random': random.choice(util.list_entries())
    }