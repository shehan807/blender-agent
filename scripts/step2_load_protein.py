"""Step 2: Load 8V00.pdb, apply space-filling spheres with AO, set per-chain colors."""
import bpy
import bl_ext.blender_org.molecularnodes as mn

PDB_PATH = "/Users/shehanparmar/Desktop/dev/work/IDEAS/static_protein/8V00.pdb"

# ─── Load molecule ───
mol = mn.Molecule.load(PDB_PATH)
mol.add_style(
    mn.StyleSpheres(),
    material=mn.material.AmbientOcclusion()
)

bpy.context.view_layer.update()

mol_obj = bpy.data.objects.get(mol._object_name)
print(f"Loaded: {mol._object_name}")
print(f"Location: {mol_obj.location}")

# Print some info about the mesh
if mol_obj and mol_obj.data:
    attrs = [a.name for a in mol_obj.data.attributes]
    print(f"Attributes: {attrs}")
    n_verts = len(mol_obj.data.vertices)
    print(f"Vertices (atoms): {n_verts}")

    # Check for chain_id attribute
    chain_attr = mol_obj.data.attributes.get('chain_id')
    if chain_attr:
        # Get unique chain IDs
        chain_ids = set()
        for i in range(len(chain_attr.data)):
            chain_ids.add(chain_attr.data[i].value)
        print(f"Chains found: {sorted(chain_ids)}")
    else:
        print("No chain_id attribute found - checking other attributes")
        for attr in mol_obj.data.attributes:
            print(f"  {attr.name}: domain={attr.domain}, data_type={attr.data_type}")

print("Protein loaded successfully")
