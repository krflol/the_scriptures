from importer import ORDERED_BOOKS, TORAH_DIR, PROPHETS_DIR, KETHUBIM_DIR, NEW_TESTAMENT_DIR


def main() -> None:
    sections = [
        ("The Tanak/The Torah", TORAH_DIR),
        ("The Tanak/Prophets", PROPHETS_DIR),
        ("The Tanak/First Warnings (Kethubim)", KETHUBIM_DIR),
        ("New Testament", NEW_TESTAMENT_DIR),
    ]

    dir_to_section = {d: name for name, d in sections}

    print("Canonical books (abbr -> Hebrew (Common)):\n")
    current_section = None
    for abbr, full_name, out_dir in ORDERED_BOOKS:
        section_name = dir_to_section.get(out_dir, "Other")
        if section_name != current_section:
            if current_section is not None:
                print()
            print(f"[{section_name}]")
            current_section = section_name
        print(f"- {abbr}: {full_name}")


if __name__ == "__main__":
    main() 