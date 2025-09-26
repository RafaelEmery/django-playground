import logging

from celery import shared_task


@shared_task
def pay_daily_payables():
    from .services import PayableService  # noqa: PLC0415

    logging.info("[payments.tasks] Starting daily payable processing...")

    service = PayableService()
    payables = service.get_today_payables()

    if not payables:
        logging.info("[payments.tasks] No payables to process today.")
        return

    for payable in payables:
        try:
            service.apply_waiting_funds_payable(payable)
        except Exception as e:
            logging.error(
                "[payments.tasks] error applying payable to balance: "
                f"payable_id - {payable.id} | error - {str(e)}"
            )
            continue

    logging.info(f"[payments.tasks] {len(payables)} payables processed.")
