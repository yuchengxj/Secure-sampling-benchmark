#include "Math/gfp.h"
#include "Math/gf2n.h"
#include "Networking/sockets.h"
#include "Networking/ssl_sockets.h"
#include "Tools/int.h"
#include "Math/Setup.h"
#include "Protocols/fake-stuff.h"

#include "Math/gfp.hpp"
#include "Client.hpp"
#include <string>
#include <sodium.h>
#include <iostream>
#include <sstream>
#include <fstream>

#define N 6012

/* One run to send and recieve values */
template<class T, class U>
void one_run(T value, Client& client)
{
    /* Send the private input to servers */
    client.send_private_inputs<T>({salary_value});
    cout << "Sent private inputs to each computing party, waiting for results..." << endl;

    /* Get the result back (maybe the next index to send) */
    U result = client.receive_outputs<T>(1)[0];

    cout << "Computing parties chose index: " << result << endl;
}

template<class T, class U>
void run(double value, Client& client)
{
    // sint
    one_run<T, U>(long(round(value)), client);

    // sfix with f = 16
    one_run<T, U>(long(round(value * exp2(16))), client);
}

template<class T, class U>
void run_estimation(string path, Client& client)
{
    ifstream ifs(path);
    if (ifs)
    {
        string line;
        vector<long> values;
        getline(ifs,line);
        for (int i = 0; i < N; ++i)
        {
            getline(ifs, line)
            values.push_back(stoi(line));   
        }
    }
    for (auto value : values)
    {
        // sint
        one_run<T, U>(long(round(value)), client);

        // sfix with f = 16
        one_run<T, U>(long(round(value * exp2(16))), client);
    }
    U result = client.receive_outputs<T>(1)[0];
    cout << "Computing parties esitmate threshold:" << result << endl;
}



int main(int argc, char** argv)
{
    int my_client_id;
    int nparties;
    string data_path;
    int finish;
    int port_base = 14000;

    if (argc < 5) {
        cout << "Usage: thrshold-publish-clients.x <client identifier> <number of spdz parties>"
            << "<path of scores> <finish (0 false, 1 true)> <optional host names..., default: local host>"
            << "<optional spdz party port base number, default 14000>" << endl;
        exit(0);
    }

    my_client_id = atoi(argv[1]);
    nparties = atoi(argv[2]);
    data_path = argv[3];
    finish = atoi(argv[4]);
    vector<string> hostnames(nparties, "localhost");

    if (argc > 5)
    {
        if (argc < 5 + nparties)
        {
            cerr << "Not enough hostnames specified";
            exit(1);
        }

        for (int i = 0; i < nparties; i++)
            hostnames[i] = argv[5 + i];
    }

    if (argc > 5 + nparties)
        port_base = atoi(argv[5 + nparties]);

    bigint::init_thread();

    /* Setup connections from this client to eahc party socket */
    Client client(hostnames, port_base, my_client_id);
    auto& specification = client.
    auto& sockets = client.sockets;

    
    for (int i = 0; i < nparties; ++i)
    {
        octetStream os;
        os.store(finish);
        os.Send(socket[i]);
    }
    cout << "Finish setup socket connection to SPDZ engines." << endl;

    int type = specification.get<int>();
        switch (type)
    {
    case 'p':
    {
        gfp::init_field(specification.get<bigint>());
        cerr << "using prime " << gfp::pr() << endl;
        run_esimation<gfp, gfp>(data_path, client);
        break;
    }
    case 'R':
    {
        int R = specification.get<int>();
        switch (R)
        {
        case 64:
            run_esimation<Z2<64>, Z2<64>>(data_path, client);
            break;
        case 104:
            run_esimation<Z2<104>, Z2<64>>(data_path, client);
            break;
        case 128:
            run_esimation<Z2<128>, Z2<64>>(data_path, client);
            break;
        default:
            run_esimation << R << "-bit ring not implemented";
            exit(1);
        }
        break;
    }
    default:
        cerr << "Type " << type << " not implemented";
        exit(1);
    }
}