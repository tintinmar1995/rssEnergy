from rssEnergy import driver, parsers

drv = driver.get_driver()

print(parsers.enedis_odte(drv))
