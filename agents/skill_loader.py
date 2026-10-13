from pathlib import Path


class SkillPackage:
    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)

        if not self.skill_dir.exists():
            raise FileNotFoundError(f"Skill directory not found: {self.skill_dir}")

        self.skill_md = self.skill_dir / "SKILL.md"
        self.references_dir = self.skill_dir / "references"
        self.scripts_dir = self.skill_dir / "scripts"

    def load_skill_instruction(self) -> str:
        if not self.skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {self.skill_dir}")

        return self.skill_md.read_text(encoding="utf-8")

    def load_references(self) -> str:
        if not self.references_dir.exists():
            return ""

        reference_texts = []

        for file_path in sorted(self.references_dir.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")
            reference_texts.append(
                f"\n\n## Reference File: {file_path.name}\n{content}"
            )

        return "\n".join(reference_texts)

    def build_context(self) -> str:
        skill_instruction = self.load_skill_instruction()
        references = self.load_references()

        return f"""
# Skill Instruction
{skill_instruction}

# Skill References
{references}
""".strip()