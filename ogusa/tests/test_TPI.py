import pytest
import pickle
import numpy as np
import os
from ogusa import SS, TPI, utils, firm
from ogusa.parameters import Specifications

CUR_PATH = os.path.abspath(os.path.dirname(__file__))


filename1 = 'intial_SS_values_baseline.pkl'
filename2 = 'intial_SS_values_reform.pkl'
filename3 = 'intial_SS_values_reform_base_spend.pkl'
param_updates1 = {}
param_updates2 = {}
param_updates3 = {'baseline_spending': True}


@pytest.mark.parametrize('baseline,param_updates,filename',
                         [(True, param_updates1, filename1),
                          (False, param_updates2, filename2),
                          (False, param_updates3, filename3)],
                         ids=['Baseline', 'Reform',
                              'Reform, baseline_spending'])
def test_get_initial_SS_values(baseline, param_updates, filename):
    p = Specifications(baseline=baseline, test=True)
    p.update_specifications(param_updates)
    p.baseline_dir = os.path.join(CUR_PATH, 'test_io_data', 'OUTPUT')
    p.output_base = os.path.join(CUR_PATH, 'test_io_data', 'OUTPUT')
    test_tuple = TPI.get_initial_SS_values(p)
    (test_initial_values, test_ss_vars, test_theta,
     test_baseline_values) = test_tuple
    import pickle
    pickle.dump(test_tuple, open(
        os.path.join(CUR_PATH, 'test_io_data', filename), 'wb'))

    expected_tuple = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', filename))

    (exp_initial_values, exp_ss_vars, exp_theta,
     exp_baseline_values) = expected_tuple

    for i, v in enumerate(exp_initial_values):
        assert(np.allclose(test_initial_values[i], v, equal_nan=True))

    if p.baseline_spending:
        for i, v in enumerate(exp_baseline_values):
            assert(np.allclose(test_baseline_values[i], v, equal_nan=True))

    assert(np.allclose(test_theta, exp_theta))

    for k, v in exp_ss_vars.items():
        assert(np.allclose(test_ss_vars[k], v, equal_nan=True))


def test_firstdoughnutring():
    # Test TPI.firstdoughnutring function.  Provide inputs to function and
    # ensure that output returned matches what it has been before.
    input_tuple = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', 'firstdoughnutring_inputs.pkl'))
    guesses, r, w, b, BQ, TR, j, params = input_tuple
    income_tax_params, tpi_params, initial_b = params
    tpi_params = tpi_params + [True]
    p = Specifications()
    (p.J, p.S, p.T, p.BW, p.beta, p.sigma, p.alpha, p.gamma, p.epsilon,
     Z, p.delta, p.ltilde, p.nu, p.g_y, p.g_n, tau_b, delta_tau,
     tau_payroll, tau_bq, p.rho, p.omega, N_tilde, lambdas,
     p.imm_rates, p.e, retire, p.mean_income_data, factor, h_wealth,
     p_wealth, m_wealth, p.b_ellipse, p.upsilon, p.chi_b, p.chi_n,
     theta, p.baseline) = tpi_params
    p.Z = np.ones(p.T + p.S) * Z

    p.tau_bq = np.ones(p.T + p.S) * 0.0
    p.tau_payroll = np.ones(p.T + p.S) * tau_payroll
    p.tau_b = np.ones(p.T + p.S) * tau_b
    p.delta_tau = np.ones(p.T + p.S) * delta_tau
    p.h_wealth = np.ones(p.T + p.S) * h_wealth
    p.p_wealth = np.ones(p.T + p.S) * p_wealth
    p.m_wealth = np.ones(p.T + p.S) * m_wealth
    p.retire = (np.ones(p.T + p.S) * retire).astype(int)
    p.tax_func_type = 'DEP'
    p.analytical_mtrs, etr_params, mtrx_params, mtry_params =\
        income_tax_params
    p.etr_params = np.transpose(etr_params, (1, 0, 2))
    p.mtrx_params = np.transpose(mtrx_params, (1, 0, 2))
    p.mtry_params = np.transpose(mtry_params, (1, 0, 2))
    p.lambdas = lambdas.reshape(p.J, 1)
    p.num_workers = 1
    bq = BQ / p.lambdas[j]
    tr = TR
    test_list = TPI.firstdoughnutring(guesses, r, w, bq, tr, theta,
                                      factor, j, initial_b, p)

    expected_list = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data',
                     'firstdoughnutring_outputs.pkl'))

    assert(np.allclose(np.array(test_list), np.array(expected_list)))


file_in1 = os.path.join(CUR_PATH, 'test_io_data',
                        'twist_doughnut_inputs_2.pkl')
file_in2 = os.path.join(CUR_PATH, 'test_io_data',
                        'twist_doughnut_inputs_S.pkl')
file_out1 = os.path.join(CUR_PATH, 'test_io_data',
                         'twist_doughnut_outputs_2.pkl')
file_out2 = os.path.join(CUR_PATH, 'test_io_data',
                         'twist_doughnut_outputs_S.pkl')


@pytest.mark.parametrize('file_inputs,file_outputs',
                         [(file_in1, file_out1), (file_in2, file_out2)],
                         ids=['s<S', 's==S'])
def test_twist_doughnut(file_inputs, file_outputs):
    '''
    Test TPI.twist_doughnut function.  Provide inputs to function and
    ensure that output returned matches what it has been before.
    '''
    input_tuple = utils.safe_read_pickle(file_inputs)
    test_list = TPI.twist_doughnut(*input_tuple)
    expected_list = utils.safe_read_pickle(file_outputs)

    assert(np.allclose(np.array(test_list), np.array(expected_list)))


@pytest.mark.full_run
def test_inner_loop():
    # Test TPI.inner_loop function.  Provide inputs to function and
    # ensure that output returned matches what it has been before.
    input_tuple = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', 'tpi_inner_loop_inputs.pkl'))
    guesses, outer_loop_vars, params, j = input_tuple
    income_tax_params, tpi_params, initial_values, ind = params
    initial_values = initial_values
    tpi_params = tpi_params
    p = Specifications()
    (p.J, p.S, p.T, p.BW, p.beta, p.sigma, p.alpha, p.gamma, p.epsilon,
     Z, p.delta, p.ltilde, p.nu, p.g_y, p.g_n, tau_b, delta_tau,
     tau_payroll, tau_bq, p.rho, p.omega, N_tilde, lambdas,
     p.imm_rates, p.e, retire, p.mean_income_data, factor, h_wealth,
     p_wealth, m_wealth, p.b_ellipse, p.upsilon, p.chi_b, p.chi_n,
     theta, p.baseline) = tpi_params
    p.eta = p.omega.reshape(p.T + p.S, p.S, 1) * p.lambdas.reshape(1, p.J)
    p.Z = np.ones(p.T + p.S) * Z
    p.tau_bq = np.ones(p.T + p.S) * 0.0
    p.tau_payroll = np.ones(p.T + p.S) * tau_payroll
    p.tau_b = np.ones(p.T + p.S) * tau_b
    p.delta_tau = np.ones(p.T + p.S) * delta_tau
    p.h_wealth = np.ones(p.T + p.S) * h_wealth
    p.p_wealth = np.ones(p.T + p.S) * p_wealth
    p.m_wealth = np.ones(p.T + p.S) * m_wealth
    p.retire = (np.ones(p.T + p.S) * retire).astype(int)
    p.tax_func_type = 'DEP'
    p.analytical_mtrs, etr_params, mtrx_params, mtry_params =\
        income_tax_params
    p.etr_params = np.transpose(etr_params, (1, 0, 2))[:p.T, :, :]
    p.mtrx_params = np.transpose(mtrx_params, (1, 0, 2))[:p.T, :, :]
    p.mtry_params = np.transpose(mtry_params, (1, 0, 2))[:p.T, :, :]
    p.lambdas = lambdas.reshape(p.J, 1)
    p.num_workers = 1
    (K0, b_sinit, b_splus1init, factor, initial_b, initial_n,
     p.omega_S_preTP, initial_debt, D0) = initial_values
    initial_values_in = (K0, b_sinit, b_splus1init, factor, initial_b,
                         initial_n, D0)
    (r, K, BQ, TR) = outer_loop_vars
    wss = firm.get_w_from_r(r[-1], p, 'SS')
    w = np.ones(p.T + p.S) * wss
    w[:p.T] = firm.get_w_from_r(r[:p.T], p, 'TPI')
    outer_loop_vars_in = (r, w, r, BQ, TR, theta)

    guesses = (guesses[0], guesses[1])
    test_tuple = TPI.inner_loop(guesses, outer_loop_vars_in,
                                initial_values_in, j, ind, p)

    expected_tuple = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', 'tpi_inner_loop_outputs.pkl'))

    for i, v in enumerate(expected_tuple):
        assert(np.allclose(test_tuple[i], v))


@pytest.mark.full_run
def test_run_TPI():
    # Test TPI.run_TPI function.  Provide inputs to function and
    # ensure that output returned matches what it has been before.
    input_tuple = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', 'run_TPI_inputs.pkl'))
    (income_tax_params, tpi_params, iterative_params, small_open_params,
     initial_values, SS_values, fiscal_params, biz_tax_params,
     output_dir, baseline_spending) = input_tuple
    tpi_params = tpi_params + [True]
    initial_values = initial_values + (0.0,)

    p = Specifications()
    (J, S, T, BW, p.beta, p.sigma, p.alpha, p.gamma, p.epsilon,
     Z, p.delta, p.ltilde, p.nu, p.g_y, p.g_n, tau_b, delta_tau,
     tau_payroll, tau_bq, p.rho, p.omega, N_tilde, lambdas,
     p.imm_rates, p.e, retire, p.mean_income_data, factor, h_wealth,
     p_wealth, m_wealth, p.b_ellipse, p.upsilon, p.chi_b, p.chi_n,
     theta, p.baseline) = tpi_params

    new_param_values = {
        'J': J,
        'S': S,
        'T': T,
        'eta': (np.ones((S, J)) / (S * J)),
        'r_gov_shift': 0.0, 'zeta_D': [0.0, 0.0],
        'zeta_K': [0.0, 0.0], 'debt_ratio_ss': 1.0,
        'initial_foreign_debt_ratio': 0.0,
        'start_year': 2019
    }
    # update parameters instance with new values for test
    p.update_specifications(new_param_values, raise_errors=False)
    (J, S, T, BW, p.beta, p.sigma, p.alpha, p.gamma, p.epsilon,
     Z, p.delta, p.ltilde, p.nu, p.g_y, p.g_n, tau_b, delta_tau,
     tau_payroll, tau_bq, p.rho, p.omega, N_tilde, lambdas,
     p.imm_rates, p.e, retire, p.mean_income_data, factor, h_wealth,
     p_wealth, m_wealth, p.b_ellipse, p.upsilon, p.chi_b, p.chi_n,
     theta, p.baseline) = tpi_params
    p.eta = p.omega.reshape(T + S, S, 1) * lambdas.reshape(1, J)
    p.Z = np.ones(p.T + p.S) * Z
    p.tau_bq = np.ones(p.T + p.S) * 0.0
    p.tau_payroll = np.ones(p.T + p.S) * tau_payroll
    p.tau_b = np.ones(p.T + p.S) * tau_b
    p.delta_tau = np.ones(p.T + p.S) * delta_tau
    p.h_wealth = np.ones(p.T + p.S) * h_wealth
    p.p_wealth = np.ones(p.T + p.S) * p_wealth
    p.m_wealth = np.ones(p.T + p.S) * m_wealth
    p.retire = (np.ones(p.T + p.S) * retire).astype(int)
    p.small_open, ss_firm_r, ss_hh_r = small_open_params
    p.ss_firm_r = np.ones(p.T + p.S) * ss_firm_r
    p.ss_hh_r = np.ones(p.T + p.S) * ss_hh_r
    p.maxiter, p.mindist_SS, p.mindist_TPI = iterative_params
    (p.budget_balance, alpha_T, alpha_G, p.tG1, p.tG2, p.rho_G,
     p.debt_ratio_ss) = fiscal_params
    p.alpha_T = np.concatenate((alpha_T, np.ones(40) * alpha_T[-1]))
    p.alpha_G = np.concatenate((alpha_G, np.ones(40) * alpha_G[-1]))
    (tau_b, delta_tau) = biz_tax_params
    p.tau_b = np.ones(p.T + p.S) * tau_b
    p.delta_tau = np.ones(p.T + p.S) * delta_tau
    p.analytical_mtrs, etr_params, mtrx_params, mtry_params =\
        income_tax_params
    p.etr_params = np.transpose(etr_params, (1, 0, 2))[:p.T, :, :]
    p.mtrx_params = np.transpose(mtrx_params, (1, 0, 2))[:p.T, :, :]
    p.mtry_params = np.transpose(mtry_params, (1, 0, 2))[:p.T, :, :]
    p.lambdas = lambdas.reshape(p.J, 1)
    p.output = output_dir
    p.baseline_spending = baseline_spending
    p.frac_tax_payroll = 0.5 * np.ones(p.T + p.S)
    p.num_workers = 1
    (K0, b_sinit, b_splus1init, factor, initial_b, initial_n,
     p.omega_S_preTP, initial_debt, D0) = initial_values

    # Need to run SS first to get results
    SS.ENFORCE_SOLUTION_CHECKS = False
    ss_outputs = SS.run_SS(p, None)

    if p.baseline:
        utils.mkdirs(os.path.join(p.baseline_dir, "SS"))
        ss_dir = os.path.join(p.baseline_dir, "SS/SS_vars.pkl")
        with open(ss_dir, "wb") as f:
            pickle.dump(ss_outputs, f)
    else:
        utils.mkdirs(os.path.join(p.output_base, "SS"))
        ss_dir = os.path.join(p.output_base, "SS/SS_vars.pkl")
        with open(ss_dir, "wb") as f:
            pickle.dump(ss_outputs, f)

    test_dict = TPI.run_TPI(p, None)

    expected_dict = utils.safe_read_pickle(
        os.path.join(CUR_PATH, 'test_io_data', 'run_TPI_outputs.pkl'))

    # delete values key-value pairs that are not in both dicts
    del expected_dict['I_total']
    del test_dict['etr_path'], test_dict['mtrx_path'], test_dict['mtry_path']
    del test_dict['bmat_s']
    test_dict['b_mat'] = test_dict.pop('bmat_splus1')
    test_dict['REVENUE'] = test_dict.pop('total_revenue')
    test_dict['T_H'] = test_dict.pop('TR')
    test_dict['IITpayroll_revenue'] = (test_dict['REVENUE'][:160] -
                                       test_dict['business_revenue'])
    del test_dict['T_P'], test_dict['T_BQ'], test_dict['T_W']
    del test_dict['y_before_tax_mat'], test_dict['K_f'], test_dict['K_d']
    del test_dict['D_d'], test_dict['D_f']
    del test_dict['new_borrowing_f'], test_dict['debt_service_f']
    del test_dict['iit_revenue'], test_dict['payroll_tax_revenue']
    del test_dict['resource_constraint_error'], test_dict['T_C']
    del test_dict['r_gov'], test_dict['r_hh'], test_dict['tr_path']

    for k, v in expected_dict.items():
        try:
            assert(np.allclose(test_dict[k], v, rtol=1e-04, atol=1e-04))
        except ValueError:
            assert(np.allclose(test_dict[k], v[:p.T, :, :], rtol=1e-04,
                               atol=1e-04))
