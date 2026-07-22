import { Card, CardContent, Typography } from "@mui/material";

function DashboardCard({ title, value }) {

    return (

        <Card
            sx={{
                borderRadius:3,
                boxShadow:3
            }}
        >

            <CardContent>

                <Typography
                    color="text.secondary"
                >
                    {title}
                </Typography>

                <Typography
                    variant="h4"
                    fontWeight="bold"
                >
                    {value}
                </Typography>

            </CardContent>

        </Card>

    );

}

export default DashboardCard;