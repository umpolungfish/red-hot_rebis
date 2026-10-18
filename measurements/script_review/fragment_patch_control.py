class RetrosyntheticNode:
    def __init__(self):
        self.reagent_match = None
        self.fragment_smiles = ""

class ReactionPipeline:
    def deep_retrosynthesis(self, target):
        route = {}
        route["child_a"] = self.deep_retrosynthesis("a", fg_hint=cut["fg1"])
        route['child_b'] = self.deep_retrosynthesis(
            "b", fg_hint=cut['fg2'])
        frag_a, frag_b = self._get_fragment_smiles_for_cut(
            cut["fg1"], cut["fg2"], cut["bond"])
        if frag_a:
            route["child_a"].fragment_smiles = frag_a
        if frag_b:
            route["child_b"].fragment_smiles = frag_b
        return route

    def _tree_to_dict(self, node):
        result = {}
        if node.fragment_smiles:
            result["fragment_smiles"] = node.fragment_smiles
        if node.reagent_match:
            result['reagent'] = node.reagent_match
        return result
