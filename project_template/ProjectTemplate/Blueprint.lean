import Verso
import VersoManual
import VersoBlueprint
import VersoBlueprint.Commands.Graph
import VersoBlueprint.Commands.Summary
import ProjectTemplate.Chapters.Addition
import ProjectTemplate.Chapters.Multiplication

open Verso.Genre
open Verso.Genre.Manual
open Informal

#doc (Manual) "Starter Blueprint" =>

This small Blueprint tracks a few basic facts about addition and multiplication
on natural numbers. It is intentionally small, so it can serve as a starting
point for a new project.

{include 0 ProjectTemplate.Chapters.Addition}
{include 0 ProjectTemplate.Chapters.Multiplication}

{blueprint_graph}
{blueprint_summary}
