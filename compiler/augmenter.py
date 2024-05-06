def augmenter(source: str) -> str:
    lines = source.split("\n")
    augmented_source = ""
    current_indentation_level = 0
    for line in lines:
        if "\t" in line:
            raise RuntimeError("No tabs allowed.")
        line = line.split("#")[0]
        indentation_spaces = 0
        for p in range(len(line)):
            if line[p] != " ":
                break
            indentation_spaces += 1
        assert indentation_spaces % 4 == 0, "Indentation is not multiple of 4."
        indentation_level = indentation_spaces // 4
        indentation_change = indentation_level - current_indentation_level
        if indentation_change > 0:
            augmented_source += "{" * indentation_change
        if indentation_change < 0:
            augmented_source += "}" * -indentation_change
        augmented_source += line.lstrip(" ")
        current_indentation_level = indentation_level
        augmented_source += ";"

    if current_indentation_level > 0:
        augmented_source += "}" * current_indentation_level
    return augmented_source
