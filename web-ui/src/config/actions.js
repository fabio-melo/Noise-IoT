import React from 'react';

import { CardActions, CreateButton, RefreshButton } from 'react-admin';

export const Actions = ({
    bulkActions,
    basePath,
    displayedFilters,
    filters,
    filterValues,
    onUnselectItems,
    resource,
    selectedIds,
    showFilter}) => (
    <CardActions>
        {bulkActions && React.cloneElement(bulkActions, {
            basePath,
            filterValues,
            resource,
            selectedIds,
            onUnselectItems,
        })}
        {filters && React.cloneElement(filters, {
            resource,
            showFilter,
            displayedFilters,
            filterValues,
            context: 'button',
        }) }
        <CreateButton basePath={basePath} />
       
        <RefreshButton label="Recarregar" />
 
    </CardActions>
);



export const NoBulkActions = ({
    basePath,
    displayedFilters,
    filters,
    filterValues,
    resource,
    showFilter}) => (
    <CardActions>
        
        {filters && React.cloneElement(filters, {
            resource,
            showFilter,
            displayedFilters,
            filterValues,
            context: 'button',
        }) }
        <CreateButton basePath={basePath} label="Criar"/>
       
        <RefreshButton label="Recarregar" />
 
    </CardActions>
);
