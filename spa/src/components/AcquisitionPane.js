import {useEffect, useState} from "react";
import Typography from '@mui/joy/Typography';
import Button from "@mui/joy/Button";
import {Grid} from "@mui/joy";
import NumericLabel from "react-pretty-numbers"

function AcquisitionPane() {
    let [avail, setAvail] = useState(null)
    let [needRefresh, setNeedRefresh] = useState(true)

    useEffect(() => {
        if (needRefresh) {
            fetch('/data/avail')
                .then(response => response.json())
                .then(data => {
                    // console.log(data);
                    setAvail(data)
                    setNeedRefresh(false)
                    if (data.running) {
                        setTimeout(() => {
                            setNeedRefresh(true);
                        }, 300);
                    }
                });
        }
    }, [needRefresh])

    const requestUpdate = () => {
        fetch('/data/update')
            .then(response => response.json())
            .then(data => {
                console.log(data);
                setNeedRefresh(true)
            });
    }

    let have_data = (avail ? avail.have_data : false)
    let first_time = (avail ? new Date(Date.parse(avail.first_time)) : 0)
    let last_time = (avail ? new Date(Date.parse(avail.last_time)) : 0)

    return (
        <>
            <Grid container spacing={1}>
                <Grid>
                    <Typography level="h3" component="h3">
                        Available Local Data
                    </Typography>
                </Grid>
            </Grid>
            {(have_data ?
                    <>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Period:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                <Typography>
                                    {(avail.first_time === "pending" ? "Pending..."
                                    : avail.first_time + " — " +  avail.last_time)}
                                </Typography>
                            </Grid>
                        </Grid>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Days in range:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                <Typography>
                                    {(avail.first_time === "pending" ? "Pending..."
                                        : <NumericLabel>{Math.ceil((last_time - first_time)/1000/3600/24)}</NumericLabel>)}
                                </Typography>
                            </Grid>
                        </Grid>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Missing days:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                <Typography>
                                    <NumericLabel>{avail.missing_days.length}</NumericLabel>
                                </Typography>
                            </Grid>
                        </Grid>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Incomplete days:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                <Typography>
                                    <NumericLabel>{avail.incomplete_days.length}</NumericLabel>
                                </Typography>
                            </Grid>
                        </Grid>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Number of records:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                <Typography>
                                    {(avail.records === "pending" ? "Pending..."
                                        : <NumericLabel>{avail.records}</NumericLabel>)}
                                </Typography>
                            </Grid>
                        </Grid>
                        <Grid container spacing={1}>
                            <Grid item xs={3}>
                                <Typography>
                                    <b>Data management log:</b>
                                </Typography>
                            </Grid>
                            <Grid>
                                {
                                    avail.log.map(
                                        (entry, i) => <Typography key={i}>{entry}</Typography>
                                    )
                                }

                            </Grid>
                        </Grid>
                    </>
                    :
                    <Grid container spacing={1}>
                        <Grid>
                            No data.
                        </Grid>

                    </Grid>
            )}
            <Grid container spacing={1}>
                <Grid>
                    <Button disabled={(avail ? avail.running : false)} onClick={() => requestUpdate()}>
                        Update from Octopus Energy
                    </Button>
                </Grid>
            </Grid>
        </>
    )
}

export default AcquisitionPane;