#
# services/order_email_template_service.py
#

class OrderEmailTemplateService:
    """
    Prepara os dados dos templates de e-mail relacionados aos pedidos.
    """

    def prepare(self, notification_type: str, data: dict) -> dict:
        """
        Prepara os dados de acordo com o tipo de notificação do pedido.

        Args:
            notification_type: Tipo da notificação recebida.
            data: Dados originais da mensagem.

        Returns:
            Dados validados e complementados para o template.

        Raises:
            ValueError: Quando faltarem dados obrigatórios.
        """

        if notification_type == 'ORDER_RECEIVED':
            return self._prepare_received(data)

        if notification_type == 'ORDER_UPDATED':
            return self._prepare_status(data, notification_type)

        if notification_type == 'ORDER_SENT':
            prepared_data = self._prepare_status(data, notification_type)
            self._validate_status(prepared_data, 'OUT_FOR_DELIVERY')
            return prepared_data

        if notification_type == 'ORDER_DELIVERED':
            prepared_data = self._prepare_status(data, notification_type)
            self._validate_status(prepared_data, 'DELIVERED')
            return prepared_data

        raise ValueError(
            f'Unsupported order notification type: {notification_type}'
        )

    def _prepare_received(self, data: dict) -> dict:
        """
        Valida os dados utilizados no e-mail de pedido recebido.

        Args:
            data: Dados publicados pelo order-service.

        Returns:
            Dados validados para renderização do template.

        Raises:
            ValueError: Quando faltarem dados obrigatórios.
        """

        # Campos mínimos necessários para montar o e-mail de 
        # pedido recebido.
        required_fields = (
            'full_name',
            'order_id',
            'items',
            'subtotal',
            'delivery_fee',
            'total'
        )

        # Identifica os campos obrigatórios não informados 
        # para detalhar o erro.
        missing_fields = [
            field
            for field in required_fields
            if data.get(field) in (None, '')
        ]

        if missing_fields:
            raise ValueError(
                'Missing ORDER_RECEIVED fields: '
                f'{", ".join(missing_fields)}.'
            )

        if not isinstance(data['items'], list) or not data['items']:
            raise ValueError(
                'ORDER_RECEIVED items must be a non-empty list.'
            )

        # Cada item também possui campos obrigatórios para ser 
        # exibido no template.
        required_item_fields = (
            'name', 'quantity', 
            'unit_price', 'total'
        )

        for item in data['items']:
            if not isinstance(item, dict) or any(
                item.get(field) in (None, '')
                for field in required_item_fields
            ):
                raise ValueError(
                    'Each ORDER_RECEIVED item must contain name, quantity, '
                    'unit_price and total.'
                )

        return data

    @classmethod
    def _prepare_status(cls,
                        data: dict,
                        notification_type: str) -> dict:
        """
        Prepara os campos comuns das notificações de status.

        Args:
            data: Dados recebidos na mensagem de status.
            notification_type: Tipo usado na mensagem de erro.

        Returns:
            Dados validados com o rótulo do status.

        Raises:
            ValueError: Quando faltar algum campo obrigatório.
        """

        # Campos comuns exigidos por todas as notificações 
        # de atualização de status.
        required_fields = (
            'full_name', 'order_id', 
            'status', 'updated_at'
        )

        # Identifica os campos obrigatórios não informados 
        # antes de preparar o e-mail.
        missing_fields = [
            field
            for field in required_fields
            if data.get(field) in (None, '')
        ]

        if missing_fields:
            raise ValueError(
                f'Missing {notification_type} fields: '
                f'{", ".join(missing_fields)}.'
            )

        # Mantém o status original e adiciona uma descrição 
        # amigável para o cliente.
        data['status_label'] = cls._get_status_label(data['status'])

        return data

    @staticmethod
    def _get_status_label(status: str) -> str:
        """
        Converte um status interno para o texto apresentado ao cliente.

        Args:
            status: Status interno do pedido.

        Returns:
            Texto amigável do status.
        """

        return {
            'RECEIVED': 'Recebido',
            'PREPARING': 'Em preparo',
            'READY': 'Pronto',
            'OUT_FOR_DELIVERY': 'Em entrega',
            'DELIVERED': 'Entregue',
            'CANCELLED': 'Cancelado'
        }.get(status, status)

    @staticmethod
    def _validate_status(data: dict, expected_status: str) -> None:
        """
        Garante que o tipo da mensagem corresponda ao status do pedido.

        Args:
            data: Dados preparados da mensagem.
            expected_status: Status exigido pelo tipo da notificação.

        Raises:
            ValueError: Quando o status recebido for incompatível.
        """

        # Impede que uma notificação específica seja enviada com 
        # status incompatível.
        if data['status'] != expected_status:
            raise ValueError(
                f"Order status must be {expected_status}."
            )
