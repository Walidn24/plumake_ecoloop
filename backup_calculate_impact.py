def calculate_impact(uuid, requested_method="EN15804+A2 (EF 3.1)"):
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize the IPC client
    try:
        client = ipc.Client(8080)  # Adjust the port if necessary
    except Exception as e:
        logging.error(f"Failed to connect to IPC server: {e}")
        exit()

    # Define the process ID
    process_id = uuid  # Replace with your actual process ID

    # Retrieve the process descriptor
    try:
        process = client.get_descriptor(o.Process, process_id)
        if not process:
            raise ValueError(f"Process with ID {process_id} not found.")
        logging.info(f"Found process: {process.name} (ID: {process_id})  (Tag: {process.category})")
    except Exception as e:
        logging.error(f"Error retrieving process: {e}")
        exit()

    # Select the first available impact method (you can refine this to pick TRACI if needed)
    try:
        methods = client.get_descriptors(o.ImpactMethod)
        # print(f"this is method: {methods}")

        if not methods:
            raise ValueError("No impact methods found in the database.")
        
        method = next((m for m in methods if requested_method in m.name), methods[0])

        logging.info(f"Using impact method: {method.name} (ID: {method.id})")
    except Exception as e:
        logging.error(f"Error retrieving impact method: {e}")
        exit()

    # Prepare the calculation setup
    setup = o.CalculationSetup(
        target=process,
        impact_method=method
    )

    # Perform the calculation
    try:
        result = client.calculate(setup)
        if result.error:
            raise ValueError(f"Calculation failed: {result.error}")
        logging.info("ready to calculate")
        logging.info(f"result: {result}")
    except Exception as e:
        logging.error(f"Error during calculation: {e}")
        exit()

    # Wait for the calculation to finish
    try:
        logging.info("Waiting for calculation to complete...")
        max_wait_time = 120  # seconds
        poll_interval = 2  # seconds
        start_time = time.time()


        while not result.wait_until_ready():
            num = num + 1
            print(f"waiting: {num}")
            if time.time() - start_time > max_wait_time:
                raise TimeoutError("Calculation did not complete within the expected time.")
            time.sleep(poll_interval)

        logging.info("Calculation completed successfully.")

        # Retrieve results
        impact_results = result.get_total_impacts()
        # flow_results = result.get_total_flows()

        # print(f'result: {impact_results, flow_results}')


    except Exception as e:
        logging.error(f"Error during or after calculation: {e}")
        result.dispose()
        exit()

    # Print impact assessment results
    try:
        print("\nImpact Assessment Results:")
        if not impact_results:
            print("No impact results available.")
        for impact in impact_results:
            print(f"{impact.impact_category.name}: {impact.amount:.5f} {impact.impact_category.ref_unit}")
            # TODO: add insert to db methods

    except Exception as e:
        logging.error(f"Error retrieving impact results: {e}")


    # Dispose result to free memory
    time.sleep(1)  # Optional pause
    result.dispose()
    logging.info("Result disposed.")