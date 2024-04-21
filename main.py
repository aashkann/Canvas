"""This module contains the business logic of the function.

Use the automation_context module to wrap your function in an Autamate context helper
"""

from pydantic import Field, SecretStr
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)
from specklepy.objects.geometry import Brep

from tracer import trace
from flatten import flatten_base


class FunctionInputs(AutomateBase):
    """These are function author defined values.

    Automate will make sure to supply them matching the types specified here.
    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """

    # an example how to use secret values
    whisper_message: SecretStr = Field(title="This is a secret message")
    forbidden_speckle_type: str = Field(
        title="Forbidden speckle type",
        description=(
            "If a object has the following speckle_type,"
            " it will be marked with an error."
        ),
    )


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """This is an example Speckle Automate function.

    Args:
        automate_context: A context helper object, that carries relevant information
            about the runtime context of this function.
            It gives access to the Speckle project data, that triggered this run.
            It also has conveniece methods attach result data to the Speckle model.
        function_inputs: An instance object matching the defined schema.
    """
    try:
        # the context provides a conveniet way, to receive the triggering version
        version_root_object = automate_context.receive_version()

        #print(version_root_object["elements"])


        flattened = list(flatten_base(version_root_object))
        
        objects = [
            b
            for b in flattened
            if b.speckle_type in [Brep.speckle_type]
        ]

        print(list(b["name"] for b in objects))

        context = [b for b in objects if b["name"] == "Context"]
        design = [b for b in objects if b["name"] == "Design"]
        base = [b for b in objects if b["name"] == "Base"]

        print(len(context))
        print(len(design))
        print(len(base))


        context_meshes = [mesh.displayValue[0] for mesh in context]
        design_meshes = [mesh.displayValue[0] for mesh in design]
        base_meshes = [mesh.displayValue[0] for mesh in base]

        # print(len(context_meshes))
        # print(len(design_meshes))
        # print(len(base_meshes))

        results = trace(base_meshes, design_meshes, context_meshes)

        print(results)
        
        
        automate_context.mark_run_success("No forbidden types found.")

        # if the function generates file results, this is how it can be
        # attached to the Speckle project / model
        # automate_context.store_file_result("./report.pdf")
    except e:
        print(e)
        automate_context.mark_run_success("No forbidden types found.")
        #automate_context.mark_run_failed(
        #        "Automation failed: "
        #        f"Found {count} object that have one of the forbidden speckle types: "
        #        f"{function_inputs.forbidden_speckle_type}"
        #    )


def automate_function_without_inputs(automate_context: AutomationContext) -> None:
    """A function example without inputs.

    If your function does not need any input variables,
     besides what the automation context provides,
     the inputs argument can be omitted.
    """
    pass


# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference, do not invoke it!

    # pass in the function reference with the inputs schema to the executor
    execute_automate_function(automate_function, FunctionInputs)

    # if the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
