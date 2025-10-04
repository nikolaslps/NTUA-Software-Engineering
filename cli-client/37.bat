@echo off
cd /d "%~dp0"

call se2437 healthcheck
call se2437 resetpasses
call se2437 healthcheck
call se2437 resetstations
call se2437 healthcheck
call se2437 admin --addpasses --source passes37.csv
call se2437 healthcheck
call se2437 tollstationpasses --station AM08 --from 20220428 --to 20220512 --format json
call se2437 tollstationpasses --station NAO04 --from 20220428 --to 20220512 --format csv
call se2437 tollstationpasses --station NO01 --from 20220428 --to 20220512 --format csv
call se2437 tollstationpasses --station OO03 --from 20220428 --to 20220512 --format csv
call se2437 tollstationpasses --station XXX --from 20220428 --to 20220512 --format csv
call se2437 tollstationpasses --station OO03 --from 20220428 --to 20220512 --format YYY
call se2437 errorparam --station OO03 --from 20220428 --to 20220512 --format csv
call se2437 tollstationpasses --station AM08 --from 20220429 --to 20220510 --format json
call se2437 tollstationpasses --station NAO04 --from 20220429 --to 20220510 --format csv
call se2437 tollstationpasses --station NO01 --from 20220429 --to 20220510 --format csv
call se2437 tollstationpasses --station OO03 --from 20220429 --to 20220510 --format csv
call se2437 tollstationpasses --station XXX --from 20220429 --to 20220510 --format csv
call se2437 tollstationpasses --station OO03 --from 20220429 --to 20220510 --format YYY
call se2437 passanalysis --stationop AM --tagop NAO --from 20220428 --to 20220512 --format json
call se2437 passanalysis --stationop NAO --tagop AM --from 20220428 --to 20220512 --format csv
call se2437 passanalysis --stationop NO --tagop OO --from 20220428 --to 20220512 --format csv
call se2437 passanalysis --stationop OO --tagop KO --from 20220428 --to 20220512 --format csv
call se2437 passanalysis --stationop XXX --tagop KO --from 20220428 --to 20220512 --format csv
call se2437 passanalysis --stationop AM --tagop NAO --from 20220429 --to 20220510 --format json
call se2437 passanalysis --stationop NAO --tagop AM --from 20220429 --to 20220510 --format csv
call se2437 passanalysis --stationop NO --tagop OO --from 20220429 --to 20220510 --format csv
call se2437 passanalysis --stationop OO --tagop KO --from 20220429 --to 20220510 --format csv
call se2437 passanalysis --stationop XXX --tagop KO --from 20220429 --to 20220510 --format csv
call se2437 passescost --stationop AM --tagop NAO --from 20220428 --to 20220512 --format json
call se2437 passescost --stationop NAO --tagop AM --from 20220428 --to 20220512 --format csv
call se2437 passescost --stationop NO --tagop OO --from 20220428 --to 20220512 --format csv
call se2437 passescost --stationop OO --tagop KO --from 20220428 --to 20220512 --format csv
call se2437 passescost --stationop XXX --tagop KO --from 20220428 --to 20220512 --format csv
call se2437 passescost --stationop AM --tagop NAO --from 20220429 --to 20220510 --format json
call se2437 passescost --stationop NAO --tagop AM --from 20220429 --to 20220510 --format csv
call se2437 passescost --stationop NO --tagop OO --from 20220429 --to 20220510 --format csv
call se2437 passescost --stationop OO --tagop KO --from 20220429 --to 20220510 --format csv
call se2437 passescost --stationop XXX --tagop KO --from 20220429 --to 20220510 --format csv
call se2437 chargesby --opid NAO --from 20220428 --to 20220512 --format json
call se2437 chargesby --opid GE --from 20220428 --to 20220512 --format csv
call se2437 chargesby --opid OO --from 20220428 --to 20220512 --format csv
call se2437 chargesby --opid KO --from 20220428 --to 20220512 --format csv
call se2437 chargesby --opid NO --from 20220428 --to 20220512 --format csv
call se2437 chargesby --opid NAO --from 20220429 --to 20220510 --format json
call se2437 chargesby --opid GE --from 20220429 --to 20220510 --format csv
call se2437 chargesby --opid OO --from 20220429 --to 20220510 --format csv
call se2437 chargesby --opid KO --from 20220429 --to 20220510 --format csv
call se2437 chargesby --opid NO --from 20220429 --to 20220510 --format csv

echo Done!
pause