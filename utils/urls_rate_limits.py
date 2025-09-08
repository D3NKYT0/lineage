URL_RATE_LIMITS_DICT = {
    # APIs DRF (versão atual)
    '/api/v1/server/players-online/':                 {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-pvp/':                        {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-pk/':                         {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-clan/':                       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-rich/':                       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-online/':                     {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-level/':                      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-ranking/':               {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-heroes/':                {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-current-heroes/':        {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/grandboss-status/':               {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/siege/':                          {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/siege-participants/':             {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/boss-jewel-locations/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    
    # APIs de administração
    '/api/v1/admin/config/':                          {'rate': '10/m', 'key': 'user', 'group': 'admin-api'},
    
    # APIs de autenticação
    '/api/v1/auth/login/':                            {'rate': '5/m', 'key': 'ip', 'group': 'auth-api'},
    '/api/v1/auth/refresh/':                          {'rate': '10/m', 'key': 'user', 'group': 'auth-api'},
    '/api/v1/auth/logout/':                           {'rate': '10/m', 'key': 'user', 'group': 'auth-api'},
    
    # APIs de usuário
    '/api/v1/user/profile/':                          {'rate': '20/m', 'key': 'user', 'group': 'user-api'},
    '/api/v1/user/change-password/':                  {'rate': '5/m', 'key': 'user', 'group': 'user-api'},
    '/api/v1/user/dashboard/':                        {'rate': '20/m', 'key': 'user', 'group': 'user-api'},
    '/api/v1/user/stats/':                            {'rate': '20/m', 'key': 'user', 'group': 'user-api'},
    
    # APIs de busca
    '/api/v1/search/character/':                      {'rate': '30/m', 'key': 'ip', 'group': 'search-api'},
    '/api/v1/search/item/':                           {'rate': '30/m', 'key': 'ip', 'group': 'search-api'},
    
    # APIs de dados do jogo
    '/api/v1/clan/':                                  {'rate': '30/m', 'key': 'ip', 'group': 'game-api'},
    '/api/v1/auction/items/':                         {'rate': '30/m', 'key': 'ip', 'group': 'game-api'},
    
    # APIs de monitoramento
    '/api/v1/health/':                                {'rate': '60/m', 'key': 'ip', 'group': 'monitoring-api'},
    '/api/v1/metrics/':                               {'rate': '10/m', 'key': 'user', 'group': 'monitoring-api'},
    '/api/v1/cache/stats/':                           {'rate': '10/m', 'key': 'user', 'group': 'monitoring-api'},

    # Outras APIs
    '/app/wallet/transfer/servidor/': {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
    '/app/wallet/transfer/jogador/':  {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
}
