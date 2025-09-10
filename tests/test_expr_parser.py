#!/usr/bin/env python3

import csv
import pytest

from parseval import ExprParser

FILENAME = 'data/spice_comsol_values.csv'

def get_csv_data(filename=FILENAME):
    with open(FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        data = [(index, *row) for index, row in enumerate(reader, start=1)]
    return data

DATA = get_csv_data(FILENAME)
IDS = [f"Row {i}" for i in range(1, len(DATA) + 1)]

class Test():
    """
    Tests for the ExprParser class, which provides COMSOL and SPICE mathematical expression parsing, generation and evaluation.
    This class uses pytest for testing.
    """

    @pytest.mark.parametrize("row_index, spice_thconf, spice_thcapf, comsol_thconf, comsol_thcapf, comsol_density", DATA, ids=IDS)
    def test_evaluation(self, row_index, spice_thconf, spice_thcapf, comsol_thconf, comsol_thcapf, comsol_density):
        """
        Compares SPICE aeval, keval to COMSOL aeval, keval.
        """
        # Example SPICE usage
        expr_parser_spice_thconf = ExprParser(expr=spice_thconf,
                                varnames=["temp"], initial_lang="spice")
        
        expr_parser_spice_thcapf = ExprParser(expr=spice_thcapf,
                                varnames=["temp"], initial_lang="spice")

        expr_parser_comsol_thconf = ExprParser(expr=comsol_thconf,
                                varnames=["T"], initial_lang="comsol")

        expr_parser_comsol_thcapf = ExprParser(expr=comsol_thcapf + '*' + comsol_density,
                                varnames=["T"], initial_lang="comsol")

        # Evaluate SPICE thermal conductivity and specific heat capacity
        res_0 = expr_parser_spice_thconf.aeval(25)
        print(f"Result (aeval): {res_0}")
        res_1 = expr_parser_spice_thconf.keval(temp=25)
        print(f"Result (keval): {res_1}")
        res_2 = expr_parser_spice_thcapf.aeval(25)
        print(f"Result (aeval): {res_2}")
        res_3 = expr_parser_spice_thcapf.keval(temp=25)
        print(f"Result (keval): {res_3}")

        # Evaluate COMSOL thermal conductivity and specific heat capacity
        res_4 = expr_parser_comsol_thconf.aeval(25 + 273.15)  # Convert 25 degrees Celsius to Kelvin
        print(f"Result (aeval): {res_4}")
        res_5 = expr_parser_comsol_thconf.keval(T=25 + 273.15)
        print(f"Result (keval): {res_5}")
        res_6 = expr_parser_comsol_thcapf.aeval(25 + 273.15)  # Convert 25 degrees Celsius to Kelvin
        print(f"Result (aeval): {res_6}")
        res_7 = expr_parser_comsol_thcapf.keval(T=25 + 273.15)
        print(f"Result (keval): {res_7}")

        assert res_0 == res_1, f"Row {row_index} failed: aeval != keval, SPICE"
        assert res_4 == res_5, f"Row {row_index} failed: aeval != keval, COMSOL"
        assert res_0 == res_4, f"Row {row_index} failed: SPICE aeval != COMSOL aeval"
        assert res_1 == res_5, f"Row {row_index} failed: SPICE keval != COMSOL keval"
        assert res_2 == res_3, f"Row {row_index} failed: aeval != keval, SPICE specific heat capacity"
        assert res_6 == res_7, f"Row {row_index} failed: aeval != keval, COMSOL specific heat capacity"
        assert res_2 == res_6, f"Row {row_index} failed: SPICE specific heat capacity aeval != COMSOL specific heat capacity aeval"
        assert res_3 == res_7, f"Row {row_index} failed: SPICE specific heat capacity keval != COMSOL specific heat capacity keval"
    
    @pytest.mark.parametrize("row_index, spice_thconf, spice_thcapf, comsol_thconf, comsol_thcapf, comsol_density", DATA, ids=IDS)
    def test_generation(self, row_index, spice_thconf, spice_thcapf, comsol_thconf, comsol_thcapf, comsol_density):
        """
        Tests the generation of SPICE and COMSOL expressions from the AST.
        """
        
        expr_parser_spice_thconf = ExprParser(expr=spice_thconf,
                                varnames=["temp"], initial_lang="spice")
        
        expr_parser_spice_thcapf = ExprParser(expr=spice_thcapf,
                                varnames=["temp"], initial_lang="spice")

        expr_parser_comsol_thconf = ExprParser(expr=comsol_thconf,
                                varnames=["T"], initial_lang="comsol")

        expr_parser_comsol_thcapf = ExprParser(expr=comsol_thcapf + '*' + comsol_density,
                                varnames=["T"], initial_lang="comsol")

        generated_comsol_thconf = expr_parser_spice_thconf.generate_comsol()
        generated_comsol_thcapf = expr_parser_spice_thcapf.generate_comsol()
        generated_spice_thconf = expr_parser_comsol_thconf.generate_spice()
        generated_spice_thcapf = expr_parser_comsol_thcapf.generate_spice()

        assert '(' + generated_comsol_thconf + ')' == comsol_thconf, f"Row {row_index} failed: expected {comsol_thconf}, got {generated_comsol_thconf}"
        assert generated_comsol_thcapf == comsol_thcapf + '*' + comsol_density, f"Row {row_index} failed: expected {comsol_thcapf + '*' + comsol_density}, got {generated_comsol_thcapf}"
        assert generated_spice_thconf == spice_thconf, f"Row {row_index} failed: expected {spice_thconf}, got {generated_spice_thconf}"
        assert generated_spice_thcapf == spice_thcapf, f"Row {row_index} failed: expected {spice_thcapf}, got {generated_spice_thcapf}"