#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
                __              __\/
              | S  \          | R  \
              \ __ |          \ __ |
              /    \          /
            /       \       /
       __ /          \ __ /            __
     | N  \          | G  \          | A  \
     \ __ |          \ __ |          \ __ |

   # # # # # # # # # # # # # # # # # # # # # #

author: CAB
website: github.com/alexcab
created: 2021-12-30
"""

from typing import Dict, Any

from keyboardAgents import KeyboardAgent
from ghostAgents import RandomGhost

from pacman import runGames
import layout


def _build_configuration() -> Dict[str, Any]:
    args = {}
    import graphicsDisplay

    args['layout'] = layout.getLayout('mediumClassic')
    args['pacman'] = KeyboardAgent()
    args['ghosts'] = [RandomGhost(1), RandomGhost(2)]
    args['display'] = graphicsDisplay.PacmanGraphics(frameTime=0.1)

    args['numGames'] = 1
    args['record'] = False
    args['catchExceptions'] = False
    args['timeout'] = 30

    return args


def main() -> None:
    args = _build_configuration()
    runGames(**args)


if __name__ == '__main__':
    main()
