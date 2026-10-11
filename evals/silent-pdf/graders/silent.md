---
type: tool_used
tool: Skill
# Any 7 Flows skill, bare or namespaced — K or a flow.
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?7flows(?:-[\w-]+)?"'
min: 0
max: 0
# Silence must hold with and without the plugin, so score both arms.
arm: both
---
