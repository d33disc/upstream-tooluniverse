Boltz Tools
===========

**Configuration File**: ``remote_tools/boltz_tools.json``
**Tool Type**: Remote
**Tools Count**: 1

This page contains all tools defined in the ``boltz_tools.json`` configuration file.

Available Tools
---------------

**boltz2_docking** (Type: RemoteTool)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perform protein-ligand docking via Boltz-2: input a protein sequence plus one or more ligands (SM...

.. dropdown:: boltz2_docking tool specification

   **Tool Information:**

   * **Name**: ``boltz2_docking``
   * **Type**: ``RemoteTool``
   * **Description**: Perform protein-ligand docking via Boltz-2: input a protein sequence plus one or more ligands (SMILES), get back predicted structures and confidence scores.

   **Parameters:**

   * ``sequence`` (string) (required)
     One-letter amino acid sequence of the target protein (FASTA format, without header).

   * ``ligands`` (array) (required)
     List of ligand definitions to dock against the protein.

   * ``recycling_steps`` (integer) (optional)
     Number of recycling steps (overfold iterations).

   * ``sampling_steps`` (integer) (optional)
     Number of sampling steps for diffusion process.

   * ``diffusion_samples`` (integer) (optional)
     How many diffusion-sampled structures to generate.

   * ``step_scale`` (number) (optional)
     Scaling factor for diffusion step size.

   * ``use_potentials`` (boolean) (optional)
     If true, omit external force-field potentials from the diffusion process.

   * ``return_structure`` (boolean) (optional)
     If false, the predicted structure will not be read or returned. Defaults to false.

   **Example Usage:**

   .. code-block:: python

      query = {
          "name": "boltz2_docking",
          "arguments": {
              "sequence": "example_value",
              "ligands": ["item1", "item2"]
          }
      }
      result = tu.run(query)


Navigation
----------

* :doc:`tools_config_index` - Back to Tools Overview
* :doc:`remote_tools` - Remote Tools Setup
