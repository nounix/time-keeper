#!/bin/bash

find . -name '*.tk' -exec sh -c "echo -n '{}: ' && grep '^E' {} | cut -d'|' -f4 | paste -sd+ | bc" \; > suma.txt